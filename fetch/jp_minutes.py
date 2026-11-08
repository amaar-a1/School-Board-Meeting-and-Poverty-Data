"""Count the meetings of each Japanese municipality's board of education (教育委員会) listed on its website.

For each municipality (fetch/jp/munis.json: code, name, official site from Wikidata): open the site, follow the
link to the board of education, then to its meetings / minutes pages (会議録, 議事録, 会議の概要, 定例会, 会議の開催状況),
and count the distinct meetings listed there (a numbered or dated 定例会 / 臨時会 / 会議). Written minutes count as
meetings. robots.txt is respected; each site is visited by one thread, with a pause between requests.
Usage: python3 jp_minutes.py OUTDIR [DEADLINE_EPOCH]
"""
import concurrent.futures as cf, html, json, os, re, sys, time, urllib.parse, urllib.request, urllib.robotparser
from collections import Counter

UA = "Mozilla/5.0 (compatible; school-board research project; github.com/amaar-a1)"
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DEADLINE = float(sys.argv[2]) if len(sys.argv) > 2 else 0
BOARD = re.compile(r"教育委員会")
MEET_LINK = re.compile(r"会議録|議事録|会議の?概要|会議結果|会議の?開催|定例会|臨時会|教育委員会会議|会議の?記録|開催状況|会議資料|議事日程|議事要旨|会議日程")
NOT_LINK = re.compile(r"総合教育会議|社会教育委員|議会|審議会|協議会|PTA|学校運営協議会|入札")
# One meeting: "第5回定例会", "令和6年第3回臨時会", "令和6年5月定例会", "5月定例教育委員会", "令和6年4月25日 教育委員会会議"
MEET = re.compile(r"(?:(令和|平成)\s*(\d+|元)\s*年度?\s*)?(?:(\d{1,2})\s*月\s*(?:(\d{1,2})\s*日)?\s*)?(?:第\s*(\d+)\s*回\s*)?(?:教育委員会)?\s*(定例会|臨時会|定例教育委員会|臨時教育委員会|教育委員会会議|定例会議|臨時会議)")
Z2H = str.maketrans("０１２３４５６７８９", "0123456789")


def fetch(url, robots, t=25):
    host = urllib.parse.urlsplit(url).netloc
    rp = robots.get(host)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(f"{urllib.parse.urlsplit(url).scheme}://{host}/robots.txt", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r: rp.parse(r.read().decode("utf-8", "ignore").splitlines())
        except Exception: rp.parse([])
        robots[host] = rp
    if not rp.can_fetch(UA, url): raise PermissionError("robots.txt")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=t) as r:
        ct = r.headers.get("Content-Type", "")
        if "html" not in ct and "text" not in ct: return r.geturl(), ""
        b = r.read(3_000_000)
        enc = (re.search(r"charset=([\w-]+)", ct) or re.search(rb'charset=["\']?([\w-]+)', b[:3000]) or [None, "utf-8"])[1]
        enc = enc.decode() if isinstance(enc, bytes) else enc
        try: return r.geturl(), b.decode(enc, "ignore")
        except LookupError: return r.geturl(), b.decode("utf-8", "ignore")


def links(base, page):
    out = []
    for href, text in re.findall(r'<a\s[^>]*?href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', page, re.S | re.I):
        t = html.unescape(re.sub(r"<[^>]+>", " ", text)); t = re.sub(r"\s+", " ", t).strip().translate(Z2H)
        u = urllib.parse.urljoin(base, html.unescape(href.strip()))
        if u.startswith("http"): out.append((u, t))
    return out


def same_site(a, b):
    ha, hb = urllib.parse.urlsplit(a).netloc.split(":")[0], urllib.parse.urlsplit(b).netloc.split(":")[0]
    root = lambda h: ".".join(h.split(".")[-3:]) if h.endswith(".jp") else ".".join(h.split(".")[-2:])
    return root(ha) == root(hb)


MEET2 = re.compile(r"(定例会|臨時会)\s*[（(]?\s*第\s*(\d+)\s*回")
ERA = re.compile(r"(令和|平成)\s*(\d+|元)\s*年")


def meetings_in(page_links, text, year=None):
    """Distinct meetings in a page's links and text, in order; an entry with no year takes the latest year heading
    above it (or the page's own year)."""
    keys, titles, ctx = set(), [], year
    for _, t in page_links + [("", x) for x in re.split(r"[\n。]", text)]:
        found = False
        for m in MEET.finditer(t):
            era, yr, mon, day, num, kind = m.groups()
            if not (mon or num): continue
            y = (1 if yr == "元" else int(yr)) + (2018 if era == "令和" else 1988) if yr else ctx
            key = (y, int(mon) if mon else None, int(day) if day else None, int(num) if num else None, "臨時" if "臨時" in kind else "定例")
            found = True
            if key not in keys: keys.add(key); titles.append(t[:80])
        if not found:
            for m in MEET2.finditer(t):
                key = (ctx, None, None, int(m.group(2)), "臨時" if "臨時" in m.group(1) else "定例")
                if key not in keys: keys.add(key); titles.append(t[:80])
        e = ERA.search(t)
        if e and not found: ctx = (1 if e.group(2) == "元" else int(e.group(2))) + (2018 if e.group(1) == "令和" else 1988)
    return keys, titles


def one(m):
    robots, out = {}, {"code": m["code"], "name": m["name"], "site": m["site"], "board": "", "pages": [], "meetings": 0, "years": {}, "examples": [], "error": ""}
    try:
        home, page = fetch(m["site"], robots); time.sleep(1)
        cand = [(u, t) for u, t in links(home, page) if BOARD.search(t) and same_site(u, home) and not NOT_LINK.search(t)]
        cand.sort(key=lambda x: (x[1] != "教育委員会", len(x[1])))
        board = None
        for u, t in cand[:3]:
            try:
                bu, bp = fetch(u, robots); time.sleep(1)
            except Exception: continue
            board = (bu, bp); break
        if not board: out["error"] = "no board link"; return out
        out["board"] = board[0]
        todo = [(u, t) for u, t in links(*board) if MEET_LINK.search(t) and not NOT_LINK.search(t) and same_site(u, board[0])]
        # a board page often links to an "教育委員会について / 会議" page first
        seen, keys, titles = set(), set(), []
        k, ts = meetings_in(links(*board), "")
        keys |= k; titles += ts
        depth = 0
        while todo and len(seen) < 8:
            u, t = todo.pop(0)
            if u in seen or u.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")): continue
            seen.add(u)
            try:
                pu, pp = fetch(u, robots); time.sleep(1)
            except Exception: continue
            pl = links(pu, pp)
            e = ERA.search(t)
            py = ((1 if e.group(2) == "元" else int(e.group(2))) + (2018 if e.group(1) == "令和" else 1988)) if e else None
            k, ts = meetings_in(pl, html.unescape(re.sub(r"<[^>]+>", "\n", pp)).translate(Z2H), py)
            if k: out["pages"].append(pu)
            keys |= k; titles += ts
            # year pages (令和6年度 会議録) under a minutes page
            for u2, t2 in pl:
                if u2 not in seen and same_site(u2, pu) and (MEET_LINK.search(t2) or re.search(r"(令和|平成)\s*\d+\s*年度?", t2)) and not NOT_LINK.search(t2):
                    todo.append((u2, t2))
        out["meetings"] = len(keys)
        out["years"] = dict(Counter(str(k[0]) for k in keys if k[0]))
        out["examples"] = titles[:5]
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return out


if __name__ == "__main__":
    munis = json.load(open("fetch/jp/munis.json", encoding="utf-8"))
    res = []
    with cf.ThreadPoolExecutor(24) as ex:
        futs = {ex.submit(one, m): m for m in munis}
        for f in cf.as_completed(futs):
            res.append(f.result())
            if len(res) % 50 == 0:
                print(len(res), "done;", sum(1 for r in res if r["meetings"]), "with meetings", flush=True)
                json.dump(res, open(f"{OUT}/jp_minutes.json", "w"), ensure_ascii=False)
            if DEADLINE and time.time() > DEADLINE:
                print("deadline reached", flush=True); ex.shutdown(cancel_futures=True); break
    json.dump(res, open(f"{OUT}/jp_minutes.json", "w"), ensure_ascii=False)
    print("finished", len(res), sum(1 for r in res if r["meetings"]), "with meetings")

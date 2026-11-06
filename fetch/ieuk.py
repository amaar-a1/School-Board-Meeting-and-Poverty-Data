# Temporary: board minutes of Irish ETBs (their own websites) and UK councils' education/children's committee
# meetings from ModernGov's public web service. Writes fetch/out/ieuk/.
import csv, json, os, re, urllib.request, urllib.parse, time, traceback, html, concurrent.futures as cf
OUT = "fetch/out/ieuk"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(url, timeout=30, n=8_000_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.read(n).decode("utf-8", "replace")

# ---- Ireland: ETB board pages -> links to minutes
ETB = {
    "City of Dublin ETB": ["https://www.cdetb.ie/about-us/board/", "https://www.cityofdublinetb.ie/"],
    "Dublin and Dún Laoghaire ETB": ["https://www.ddletb.ie/minutes/"],
    "Cavan and Monaghan ETB": ["https://www.cmetb.ie/cmetb-board/"],
    "Cork ETB": ["https://www.corketb.ie/about-cork-etb/", "https://www.corketb.ie/board/"],
    "Donegal ETB": ["https://www.donegaletb.ie/donegal-etb/board-members/", "https://www.donegaletb.ie/donegal-etb/about-us/"],
    "Galway and Roscommon ETB": ["https://www.gretb.ie/about-us/board/"],
    "Kerry ETB": ["https://kerryetb.ie/board/"],
    "Kildare and Wicklow ETB": ["https://kwetb.ie/about-us-2/governance/", "https://kwetb.ie/about-us-2/publications/"],
    "Kilkenny and Carlow ETB": ["https://kcetb.ie/en/corporate/board-members/", "https://kcetb.ie/en/about-us/"],
    "Limerick and Clare ETB": ["https://lcetb.ie/board/", "https://lcetb.ie/governance/"],
    "Longford and Westmeath ETB": ["https://www.lwetb.ie/", "https://lwetb.ie/about-us/board/"],
    "Louth and Meath ETB": ["https://www.lmetb.ie/about-us/board/"],
    "Laois and Offaly ETB": ["https://loetb.ie/board/", "https://loetb.ie/organisation-support-development/corporate-services/board-and-committees/"],
    "Mayo, Sligo and Leitrim ETB": ["https://msletb.ie/about-us/corporate/board-members/", "https://msletb.ie/about-us/corporate/"],
    "Tipperary ETB": ["https://www.tipperaryetb.ie/about-us/board/"],
    "Waterford and Wexford ETB": ["https://www.wwetb.ie/about/organisation/the-board-of-wwetb/"],
}
def etb(name, urls):
    found, pages, errs = {}, [], []
    todo = list(urls)
    seen = set()
    while todo and len(seen) < 12:
        u = todo.pop(0)
        if u in seen: continue
        seen.add(u)
        try:
            s, final, t = get(u)
        except Exception as e:
            errs.append(f"{u} {e}"); continue
        pages.append(final)
        for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', t, re.I | re.S):
            href = urllib.parse.urljoin(final, html.unescape(m.group(1))); text = re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
            blob = f"{href} {text}"
            if re.search(r"minute", blob, re.I) and re.search(r"\.pdf|\.docx?|download|/wp-content/|minutes-", href, re.I):
                found[href] = text
            elif re.search(r"minute|board-meeting|board meeting", blob, re.I) and urllib.parse.urlparse(href).netloc == urllib.parse.urlparse(final).netloc and href not in seen:
                todo.append(href)
        time.sleep(1.5)
    return {"pages": pages, "errors": errs, "minutes": found}
ie = {}
for name, urls in ETB.items():
    try: ie[name] = etb(name, urls)
    except Exception: ie[name] = {"error": traceback.format_exc()[-500:]}
    log.write(f"{name}: {len(ie[name].get('minutes', {}))} minutes links; pages {ie[name].get('pages')}; errors {ie[name].get('errors')}\n"); log.flush()
json.dump(ie, open(f"{OUT}/ie_minutes.json", "w"), ensure_ascii=False, indent=1)

# ---- UK: find each council's ModernGov site, then its education / children's committees and their meetings
councils = [r for r in csv.DictReader(open("fetch/uk.csv", encoding="utf-8"))]
def slugs(n):
    base = re.sub(r"\b(council|county|city of|city|borough|royal|metropolitan|district|and|the|of)\b", " ", n.lower())
    base = re.sub(r"[^a-z ]", "", base).split()
    s1 = "".join(base); s2 = "-".join(base)
    full = re.sub(r"[^a-z]", "", n.lower())
    return list(dict.fromkeys([s1, s2, full, base[0] if base else s1]))
def probe(row):
    n = row["District"]
    for sl in slugs(n):
        for host in (f"democracy.{sl}.gov.uk", f"{sl}.moderngov.co.uk", f"moderngov.{sl}.gov.uk", f"committees.{sl}.gov.uk",
                     f"democracy.{sl}.gov.wales", f"{sl}.cmis.uk.com", f"meetings.{sl}.gov.uk", f"modgov.{sl}.gov.uk", f"councillors.{sl}.gov.uk"):
            try:
                s, final, t = get(f"https://{host}/mgWebService.asmx/GetCommittees?lCommitteeType=0", timeout=12)
                if "<committee" in t.lower():
                    return host, t
            except Exception:
                pass
    return None, ""
EDU = re.compile(r"children|education|school|learning|young people|families|lifelong|skills", re.I)
res = {}
with cf.ThreadPoolExecutor(8) as ex:
    for row, (host, t) in zip(councils, ex.map(probe, councils)):
        res[row["District ID"]] = {"council": row["District"], "host": host, "committees": []}
        if not host: continue
        for m in re.finditer(r"<committee>(.*?)</committee>", t, re.S | re.I):
            cid = re.search(r"<committeeid>(\d+)</committeeid>", m.group(1), re.I); ttl = re.search(r"<committeetitle>(.*?)</committeetitle>", m.group(1), re.I | re.S)
            dead = re.search(r"<isdeleted>(true|1)</isdeleted>", m.group(1), re.I)
            if cid and ttl and EDU.search(html.unescape(ttl.group(1))):
                res[row["District ID"]]["committees"].append({"id": cid.group(1), "title": html.unescape(ttl.group(1)).strip(), "deleted": bool(dead)})
log.write(f"UK: ModernGov found for {sum(1 for v in res.values() if v['host'])} of {len(res)} councils\n"); log.flush()
for did, v in res.items():
    for c in v["committees"]:
        try:
            s, final, t = get(f"https://{v['host']}/mgWebService.asmx/GetMeetings?lCommitteeId={c['id']}&sFromDate=01/01/2010&sToDate=31/12/2026", timeout=30)
            c["meetings"] = [html.unescape(x) for x in re.findall(r"<meetingdate>(.*?)</meetingdate>", t, re.I)]
            c["meetings_raw"] = len(re.findall(r"<meeting>", t, re.I))
        except Exception as e:
            c["error"] = str(e)[:200]
        time.sleep(0.5)
json.dump(res, open(f"{OUT}/uk_moderngov.json", "w"), ensure_ascii=False, indent=1)
log.write("UK committees: " + str(sum(len(v["committees"]) for v in res.values())) + "\n")
log.close()

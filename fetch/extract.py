# Temporary: minutes links on Irish ETBs' minutes pages (Limerick and Clare by year, Kerry, Kilkenny and Carlow).
import json, os, re, html, time, urllib.request, urllib.parse
OUT = "fetch/out/ie2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
pages = {"Limerick and Clare ETB": ["https://lcetb.ie/board-meeting-minutes-2024-2-2/", "https://lcetb.ie/board-meeting-minutes-2024-2/", "https://lcetb.ie/board-meeting-minutes-2024/",
                                    "https://lcetb.ie/board-meeting-minutes-2023/", "https://lcetb.ie/board-meeting-minutes-2022/", "https://lcetb.ie/board-meeting-minutes-2021-2/",
                                    "https://lcetb.ie/board-meeting-minutes/", "https://lcetb.ie/category/board-meeting-minutes/"],
         "Kerry ETB": ["https://kerryetb.ie/board/minutes-downloads/"],
         "Kilkenny and Carlow ETB": ["https://kcetb.ie/corporate/board-members/minutes-of-kcetb-meetings/"]}
res = {}
for etb, us in pages.items():
    found, log = {}, []
    for u in us:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r: t = r.read().decode("utf-8", "replace"); final = r.geturl()
            n = 0
            for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', t, re.I | re.S):
                href = urllib.parse.urljoin(final, html.unescape(m.group(1))); text = re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
                if re.search(r"\.pdf|\.docx?|download", href, re.I) and re.search(r"minute|board|meeting", href + " " + text, re.I):
                    found[href] = html.unescape(text); n += 1
            log.append(f"{u} {n}")
        except Exception as e:
            log.append(f"{u} ERR {e}")
        time.sleep(2)
    res[etb] = {"minutes": found, "log": log}
json.dump(res, open(f"{OUT}/ie_minutes2.json", "w"), ensure_ascii=False, indent=1)

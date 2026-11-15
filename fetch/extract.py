# Temporary: MEXT school code list (学校コード): find the download links.
import os, re, html, urllib.request
OUT = "fetch/out/mext1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for u in ["https://www.mext.go.jp/b_menu/toukei/mext_01087.html", "https://www.mext.go.jp/a_menu/other/mext_01087.html", "https://edu-data.jp/"]:
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "replace")
        title = re.search(r"<title>(.*?)</title>", t, re.S)
        links = [(html.unescape(re.sub("<[^>]+>", "", m.group(2))).strip()[:60], m.group(1)) for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)]
        keep = [l for l in links if re.search(r"\.(csv|xlsx?|zip)|コード|code", l[0] + l[1], re.I)]
        log.write(f"OK {u} | {title.group(1).strip() if title else ''}\n" + "\n".join(f"   {a} -> {b}" for a, b in keep[:40]) + "\n")
    except Exception as e: log.write(f"ERR {u} {str(e)[:100]}\n")
log.close()

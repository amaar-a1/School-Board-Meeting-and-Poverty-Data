import os, re, html, urllib.request
OUT = "fetch/out/disc10"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for name, u in [("rs_21111", "https://www.regionalstatistik.de/genesis/online?operation=statistic&levelindex=0&levelid=&code=21111"),
                ("rs_find", "https://www.regionalstatistik.de/genesis/online?operation=find&suchanweisung_language=de&query=Sch%C3%BCler+Tr%C3%A4gerschaft"),
                ("destatis_21111", "https://www-genesis.destatis.de/datenbank/online/statistic/21111/table/21111-0011")]:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read().decode("utf-8", "replace")
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", b, flags=re.S))))
        log.write(f"== {name} OK {len(b)}\n")
        for m in re.finditer(r"(21111-[0-9A-Za-z-]+)\s+([^|]{0,220})", t): log.write(f"  {m.group(1)} {m.group(2)[:220]}\n")
        log.write(t[:1500] + "\n\n")
    except Exception as e: log.write(f"== {name} ERR {e}\n")

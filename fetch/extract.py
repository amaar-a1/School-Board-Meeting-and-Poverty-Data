import os, re, html, urllib.request
OUT = "fetch/out/disc11"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for name, u in [("tab", "https://www.regionalstatistik.de/genesis/online?operation=table&code=21111-01-03-4&bypass=true&levelindex=0&levelid="),
                ("vars", "https://www.regionalstatistik.de/genesis/online?operation=statistic&levelindex=0&levelid=&code=21111&option=variables"),
                ("find2", "https://www.regionalstatistik.de/genesis/online?operation=find&suchanweisung_language=de&query=Privatschulen")]:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read().decode("utf-8", "replace")
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", b, flags=re.S))))
        i = t.find("Startseite"); log.write(f"== {name} OK\n{t[i:i+5000]}\n\n")
    except Exception as e: log.write(f"== {name} ERR {e}\n")

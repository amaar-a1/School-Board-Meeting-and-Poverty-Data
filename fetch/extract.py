import os, urllib.request
OUT = "fetch/out/estat8"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
for label, sid in [("cs_total", "000040393527"), ("cs_private", "000040393530")]:
    u = f"https://www.e-stat.go.jp/stat-search/file-download?&statInfId={sid}&fileKind=0"
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "school-board research project"}), timeout=120).read()
        open(f"{OUT}/{label}_{sid}.xlsx", "wb").write(b); log.write(f"GOT {label} {sid} {len(b)}\n")
    except Exception as e: log.write(f"ERR {label} {e}\n")

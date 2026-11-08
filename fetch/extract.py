# Temporary: Japan's 2024 welfare tables; a test run of the board-of-education minutes count on 60 municipalities.
import json, os, shutil, subprocess, sys, time, urllib.request
OUT = "fetch/out/pij5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for fid in ("000040417776", "000040434528"):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://www.e-stat.go.jp/stat-search/file-download?statInfId={fid}&fileKind=0", headers=UA), timeout=300) as r: b = r.read()
        ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "csv"
        open(f"{OUT}/jp_w_{fid}.{ext}", "wb").write(b); log.write(f"{fid} {len(b)}\n")
    except Exception as e: log.write(f"{fid} ERR {e}\n")
    time.sleep(2)
shutil.copy("fetch/jp/munis_test.json", "fetch/jp/munis_run.json")
src = open("fetch/jp_minutes.py").read().replace('"fetch/jp/munis.json"', '"fetch/jp/munis_run.json"')
open("fetch/jp_minutes_run.py", "w").write(src)
r = subprocess.run([sys.executable, "fetch/jp_minutes_run.py", OUT, str(time.time() + 3000)], capture_output=True, text=True, timeout=3300)
log.write(r.stdout[-5000:] + "\n---\n" + r.stderr[-3000:]); log.close()

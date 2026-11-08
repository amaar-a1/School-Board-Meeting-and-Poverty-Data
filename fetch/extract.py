# Temporary: Japan's borders (official N03, simplified, smartnews-smri/japan-topography); the board-of-education minutes count for all 1,741 municipalities.
import json, os, shutil, subprocess, sys, time, urllib.request
OUT = "fetch/out/pij7"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for fid in ():
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://www.e-stat.go.jp/stat-search/file-download?statInfId={fid}&fileKind=0", headers=UA), timeout=300) as r: b = r.read()
        ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "csv"
        open(f"{OUT}/jp_w_{fid}.{ext}", "wb").write(b); log.write(f"{fid} {len(b)}\n")
    except Exception as e: log.write(f"{fid} ERR {e}\n")
    time.sleep(2)
for u, fn in [] and [("https://raw.githubusercontent.com/smartnews-smri/japan-topography/main/data/municipality/geojson/s0010/N03-21_210101.json", "jp_n03_s0010.json"),
              ("https://raw.githubusercontent.com/smartnews-smri/japan-topography/main/data/municipality/geojson/s0001/N03-21_210101.json", "jp_n03_s0001.json")]:
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: b = r.read()
        open(f"{OUT}/{fn}", "wb").write(b); log.write(f"{fn} {len(b)}\n")
    except Exception as e: log.write(f"{fn} ERR {e}\n")
shutil.copy("fetch/jp/munis.json", "fetch/jp/munis_run.json")  # full run
src = open("fetch/jp_minutes.py").read().replace('"fetch/jp/munis.json"', '"fetch/jp/munis_run.json"')
open("fetch/jp_minutes_run.py", "w").write(src)
r = subprocess.run([sys.executable, "fetch/jp_minutes_run.py", OUT, str(time.time() + 4.8 * 3600)], capture_output=True, text=True, timeout=5.2 * 3600)
log.write(r.stdout[-5000:] + "\n---\n" + r.stderr[-3000:]); log.close()

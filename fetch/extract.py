# Temporary: MEXT school code list, 2026 (provisional, 1 May 2026; csv of 25 Aug 2026): download and describe.
import csv, io, os, urllib.request, collections, json
OUT = "fetch/out/mext2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for name in ("20260825-mxt_chousa01-000011635_2-1.csv", "20260825-mxt_chousa01-000011635_2-2.csv"):
    try:
        b = urllib.request.urlopen(urllib.request.Request("https://www.mext.go.jp/content/" + name, headers=UA), timeout=120).read()
        for enc in ("utf-8-sig", "cp932"):
            try: t = b.decode(enc); break
            except UnicodeDecodeError: continue
        rows = list(csv.reader(io.StringIO(t)))
        log.write(f"{name}: {len(rows)} rows, enc {enc}\n  header {rows[0]}\n  " + "\n  ".join(str(r) for r in rows[1:6]) + "\n")
        open(f"{OUT}/{name}", "w", encoding="utf-8").write(t)
        h = rows[0]
        for c in range(len(h)):
            vals = collections.Counter(r[c] for r in rows[1:] if len(r) > c)
            if len(vals) < 15: log.write(f"  col {c} {h[c]}: {dict(vals)}\n")
    except Exception as e: log.write(f"ERR {name} {e}\n")
log.close()

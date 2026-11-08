# Temporary: DGEEC "Regiões em Números 2024/2025" (ReNE2025): every region's XLSX volume, summarised to pupils by
# municipality (pre-school, 1st-3rd cycle; public and private, and public only; every school year in the files).
import io, json, os, re, subprocess, sys, time, traceback, urllib.request, zipfile
OUT = "fetch/out/pt_rene"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openpyxl"], check=False)
import openpyxl
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
links = [l[0] for l in json.load(open("fetch/out/pt_dgeec4/browse.json"))["links"] if "ficheiros" in (l[0] or "")]
vols, got = {}, set()
for href in links[:40]:
    try:
        with urllib.request.urlopen(urllib.request.Request(href, headers=UA), timeout=300) as r:
            cd = r.headers.get("Content-Disposition", ""); name = (re.search(r'filename="?([^";]+)', cd) or [None, ""])[1]
            if not (name.startswith("ReNE2025") and name.endswith("_XLSX.zip")): continue
            vols[name] = r.read(); log.write(f"got {name} {len(vols[name])}\n")
    except Exception as e: log.write(f"ERR {href} {str(e)[:60]}\n")
    time.sleep(0.5)
num = lambda v: int(v) if isinstance(v, (int, float)) else (int(str(v).replace(" ", "")) if str(v).strip().replace(" ", "").isdigit() else 0)
res = []
for vname, b in vols.items():
    z = zipfile.ZipFile(io.BytesIO(b))
    for f in z.namelist():
        if not f.endswith(".xlsx") or "/_" in f or f.split("/")[-1].startswith("_"): continue
        try:
            wb = openpyxl.load_workbook(io.BytesIO(z.read(f)), read_only=True, data_only=True)
            out = {"volume": vname, "file": f}
            for sheet, key in (("Alunos PP", "all"), ("Alunos P", "public")):
                if sheet not in wb.sheetnames: continue
                rows = [r for r in wb[sheet].iter_rows(values_only=True)]
                yi = next(i for i, r in enumerate(rows) if r and any(isinstance(c, str) and re.fullmatch(r"\d{4}/\d{2}", c.strip()) for c in r if c))
                years = [str(c).strip() for c in rows[yi] if c and re.fullmatch(r"\d{4}/\d{2}", str(c).strip())]
                start = next(j for j, c in enumerate(rows[yi]) if c and str(c).strip() == years[0])
                out["name"] = str(rows[yi + 1][0]).strip()
                d = {}
                for r in rows[yi + 1:]:
                    lab = str(r[0] or "").strip()
                    k = {"Educação pré-escolar": "pre", "1.º Ciclo": "c1", "2.º Ciclo": "c2", "3.º Ciclo": "c3"}.get(lab)
                    if k and k not in d: d[k] = {y: num(r[start + i]) for i, y in enumerate(years) if start + i < len(r)}
                out[key] = d
            res.append(out)
        except Exception as e: log.write(f"parse ERR {f} {traceback.format_exc()[-200:]}\n")
json.dump(res, open(f"{OUT}/pt_pupils_rene2025.json", "w"), ensure_ascii=False)
log.write(f"volumes {len(vols)}; municipalities {len(res)}\n")
log.close()

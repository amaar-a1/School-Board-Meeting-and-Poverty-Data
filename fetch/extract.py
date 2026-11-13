# Temporary: DepEd historical enrollment (data.gov.ph API): download the 3 XLSX resources and describe them.
import io, json, os, subprocess, sys, urllib.parse, urllib.request
OUT = "fetch/out/ph_deped5"; os.makedirs(OUT, exist_ok=True)
try:
    import openpyxl
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "openpyxl"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
d = json.loads(get("https://api.data.gov.ph/api/public/dataset/Historical%20Enrollment%20Data/l6xdlzdg-ixdr-yuve-tw7k-0cgug0ceul10"))
for i, r in enumerate(d["data"]["resources"]):
    log.write(json.dumps({k: v for k, v in r.items() if k in ("name", "url", "format", "size", "fileName", "file")}, ensure_ascii=False)[:600] + "\n")
    u = r.get("url") or ""
    if not u.startswith("http"): continue
    try:
        b = get(u.replace(" ", "%20")); fn = f"{OUT}/{i}.xlsx"; open(fn, "wb").write(b)
        wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
        log.write(f"  {len(b)} bytes, sheets {wb.sheetnames}\n")
        ws = wb[wb.sheetnames[0]]
        for row in ws.iter_rows(min_row=1, max_row=8, values_only=True): log.write("   " + json.dumps([str(c)[:25] if c is not None else None for c in row[:20]], ensure_ascii=False) + "\n")
        log.write(f"  rows {ws.max_row}\n")
    except Exception as e: log.write(f"  ERR {e}\n")
log.close()

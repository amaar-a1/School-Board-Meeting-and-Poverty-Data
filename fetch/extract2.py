# Round 19: Georgia (council meetings on YouTube; Geostat social-protection xlsx files), Korea (KESS file by province).
import os, re, json, subprocess, sys, urllib.request, urllib.parse, time
OUT = "fetch/out/five19"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
def get(n, u, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
p = subprocess.Popen([sys.executable, "fetch/ge_yt.py", OUT], stdout=open(f"{OUT}/ge_log.txt", "w"), stderr=subprocess.STDOUT)
# Korea: the province file on KESS (post 6731854)
b = get("kr_kess_post.html", "https://kess.kedi.re.kr/post/6731854?itemCode=04&menuId=m_02_04_03_01")
ids = sorted(set(re.findall(r"/userfile/(\d+)", (b or b"").decode("utf-8", "replace"))))
log.write(f"   kr userfile ids {ids}\n")
for i in ids[:3]:
    get(f"kr_userfile_{i}.bin", f"https://kess.kedi.re.kr/userfile/{i}", {"Referer": "https://kess.kedi.re.kr/post/6731854?itemCode=04&menuId=m_02_04_03_01"})
# Georgia: the social-protection pages (the subsistence allowance by municipality)
for cid in [55, 56, 57, 58, 60, 61, 62, 192]:
    b = get(f"ge_cat{cid}.html", f"https://www.geostat.ge/en/modules/categories/{cid}/x")
    if not b: continue
    t = b.decode("utf-8", "replace")
    log.write(f"   title {''.join(re.findall(r'<title>([^<]*)', t))[:80]}\n")
    for x in sorted(set(re.findall(r'https?://(?:www\.)?geostat\.ge/media/\d+/[^"\'\s<>]+\.(?:xlsx|xls|XLSX|XLS)', t))):
        log.write(f"   ge xlsx {x}\n")
        if re.search(r"subsist|allowance|assistance|social|municipal|poverty|beneficiar", x, re.I):
            get(f"ge_c{cid}_" + re.sub(r"[^A-Za-z0-9.]", "_", x.split("/")[-1])[-70:], x)
p.wait()

# Temporary: HDX COD population statistics for the Philippines, all admin levels, 2022-2025 (one workbook).
import os, urllib.request
OUT = "fetch/out/ph9"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
u = "https://data.humdata.org/dataset/5a466c38-32a2-47de-ba36-70530505df98/resource/ee2a8606-6328-42e6-8ecb-2d14c04bceb6/download/phl_admpop_2022_2023_2024_2025_v2.xlsx"
with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=600) as r: open(f"{OUT}/phl_admpop.xlsx", "wb").write(r.read())

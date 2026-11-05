# Temporary: Figure.NZ chart of school students by regional council (title, year, source).
import os, urllib.request
OUT = "fetch/out/nz"; os.makedirs(OUT, exist_ok=True)
for name, u in (("chart.html", "https://figure.nz/chart/POTlO8r1L2X6mKJc"), ("chart_api.json", "https://figure.nz/api/v1/charts/POTlO8r1L2X6mKJc")):
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (school-board research)"}), timeout=60).read()
        open(f"{OUT}/{name}", "wb").write(d)
    except Exception as e:
        open(f"{OUT}/{name}.err", "w").write(str(e))

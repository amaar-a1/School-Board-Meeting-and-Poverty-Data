import os, urllib.request, urllib.parse, json
OUT = "fetch/out/nrw"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
B = "https://www.landesdatenbank.nrw.de/ldbnrwws/rest/2020/"
def go(name, path, params, post=False):
    q = urllib.parse.urlencode(params)
    try:
        if post:
            req = urllib.request.Request(B + path, data=q.encode(), headers=dict(UA, **{"Content-Type": "application/x-www-form-urlencoded"}))
        else:
            req = urllib.request.Request(B + path + "?" + q, headers=UA)
        b = urllib.request.urlopen(req, timeout=300).read()
        open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"== {name} OK {len(b)}\n{b[:1500].decode('latin-1')}\n\n")
    except Exception as e:
        log.write(f"== {name} ERR {e} {getattr(e, 'read', lambda: b'')()[:500]}\n")
cred = {"username": "GAST", "password": "GAST", "language": "de"}
go("meta.json", "metadata/table", dict(cred, name="21111-0710i"))
for rv in ("KREISE", "GEMEIN"):
    p = dict(cred, name="21111-0710i", area="all", format="ffcsv", compress="false", startyear="2025", regionalvariable=rv, regionalkey="05*")
    go(f"t_{rv}_get.csv", "data/tablefile", p)
    go(f"t_{rv}_post.csv", "data/tablefile", p, post=True)

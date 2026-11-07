# Temporary: borders of municipalities created recently, from official sources.
# Mexico: INEGI's Marco Geoestadístico web service (wscatgeo), one municipality per request.
# Spain: IGN's INSPIRE WFS of administrative units, features in a small box around each town.
import json, os, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/gaps2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()

MX = ["17034", "07125", "17036", "02006", "04012", "17035"]
def mexico():
    out = []
    for c in MX:
        ent, mun = c[:2], c[2:]
        got = False
        for u in [f"https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgem/{ent}{mun}",
                  f"https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgem/{ent}/{mun}",
                  f"https://gaia.inegi.org.mx/wscatgeo/geo/mgem/{ent}{mun}",
                  f"https://gaia.inegi.org.mx/wscatgeo/geo/mgem/{ent}/{mun}"]:
            try:
                st, ct, b = get(u)
                open(f"{OUT}/mx_{c}_{len(out)}.raw", "wb").write(b)
                out.append(f"{c} {u} -> {st} {ct} {len(b)} bytes: {b[:160]!r}")
                if st == 200 and b[:1] in (b"{", b"[") and b'"coordinates"' in b:
                    open(f"{OUT}/mx_{c}.json", "wb").write(b); got = True; break
            except Exception as e:
                out.append(f"{c} {u} -> ERR {str(e)[:150]}")
            time.sleep(1)
        if not got: out.append(f"{c}: no geometry")
    return "\n".join(out)
step("Mexico: INEGI wscatgeo", mexico)

ES = {"ES-41904": (-5.81, 37.06), "ES-18077": (-3.85, 36.95), "ES-14901": (-5.13, 37.68), "ES-14902": (-4.85, 37.63),
      "ES-21902": (-6.88, 37.69), "ES-11903": (-5.32, 36.35), "ES-18916": (-3.48, 36.70), "ES-48916": (-2.815, 43.218)}
WFS = "https://www.ign.es/wfs-inspire/unidades-administrativas"
def spain():
    out = []
    try:
        st, ct, b = get(WFS + "?service=WFS&request=GetCapabilities", 60)
        open(f"{OUT}/es_caps.xml", "wb").write(b); out.append(f"capabilities {st} {ct} {len(b)}")
    except Exception as e: out.append(f"capabilities ERR {str(e)[:150]}")
    for did, (x, y) in ES.items():
        d = 0.06
        for fmt in ["application/json", None]:
            q = {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "typenames": "au:AdministrativeUnit",
                 "srsName": "urn:ogc:def:crs:EPSG::4326", "bbox": f"{y-d},{x-d},{y+d},{x+d},urn:ogc:def:crs:EPSG::4326", "count": "60"}
            if fmt: q["outputFormat"] = fmt
            try:
                st, ct, b = get(WFS + "?" + urllib.parse.urlencode(q), 180)
                ext = "json" if b[:1] == b"{" else "xml"
                open(f"{OUT}/es_{did}.{ext}", "wb").write(b)
                out.append(f"{did} fmt={fmt} -> {st} {ct} {len(b)} bytes: {b[:120]!r}")
                if st == 200 and len(b) > 2000 and b"Exception" not in b[:600]: break
            except Exception as e:
                out.append(f"{did} fmt={fmt} -> ERR {str(e)[:150]}")
            time.sleep(2)
    return "\n".join(out)
step("Spain: IGN INSPIRE WFS", spain)
log.close()

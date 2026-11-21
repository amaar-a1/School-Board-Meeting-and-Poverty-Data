"""Israel: OSM administrative boundaries (Geofabrik extract). Argentina: IGN provinces, simplified."""
import json, sys, urllib.request
out = sys.argv[1]
def rnd(c): return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 5), round(c[1], 5)]
import osmium, shapely.wkb
from shapely.geometry import mapping, shape
pbf = "/tmp/il.osm.pbf"
urllib.request.urlretrieve("https://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf", pbf)
wkb = osmium.geom.WKBFactory(); feats = []
class H(osmium.SimpleHandler):
    def area(self, a):
        t = a.tags
        if t.get("boundary") != "administrative" or t.get("admin_level") not in ("4", "5", "6", "7", "8", "9"): return
        try: g = shapely.wkb.loads(wkb.create_multipolygon(a), hex=True)
        except Exception: return
        g = g.simplify(0.0008, preserve_topology=True)
        p = {k: t.get(k, "") for k in ("name", "name:he", "name:en", "name:ar", "admin_level", "ref", "wikidata", "official_name")}
        p.update(osm_id=a.orig_id(), from_way=a.from_way())
        m = mapping(g); m["coordinates"] = rnd(m["coordinates"])
        feats.append({"type": "Feature", "properties": p, "geometry": m})
H().apply_file(pbf, locations=True)
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{out}/il_osm_admin.geojson", "w"), ensure_ascii=False)
print("israel admin features", len(feats))
req = urllib.request.Request("https://wms.ign.gob.ar/geoserver/ign/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ign:provincia&outputFormat=application/json",
                             headers={"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"})
d = json.load(urllib.request.urlopen(req, timeout=600))
for f in d["features"]:
    m = mapping(shape(f["geometry"]).simplify(0.004, preserve_topology=True)); m["coordinates"] = rnd(m["coordinates"]); f["geometry"] = m
json.dump(d, open(f"{out}/ar_ign_prov.json", "w"), ensure_ascii=False)
print("argentina provinces", len(d["features"]))

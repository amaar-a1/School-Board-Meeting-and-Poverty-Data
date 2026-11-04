"""Land area (km²) of GeoJSON polygons on a sphere; used for the estimated locales."""
import math

R = 6371.0088


def ring_area(ring):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(a) * R * R / 2


def area_km2(geom):
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    return sum(ring_area(p[0]) - sum(ring_area(h) for h in p[1:]) for p in polys)

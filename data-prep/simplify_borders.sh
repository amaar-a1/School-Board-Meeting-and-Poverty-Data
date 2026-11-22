#!/bin/sh
# Two levels of detail for the most detailed borders: the map draws <name>.json (simplified) when zoomed out and loads
# <name>-hi.json (the full detail) for the area in view when zoomed in (docs/map.js). Run after build_latam.py has
# written these countries' map files (and after any change to Canada's), then data-prep/map_index.py.
# Simplification is topology-aware (shared edges stay shared; keep-shapes keeps every small district). Needs mapshaper
# (npm install mapshaper).
set -e
cd "$(dirname "$0")/../docs/data/map"
MS=${MAPSHAPER:-mapshaper}
for x in "india 12%" "costa_rica 10%" "south_africa 25%" "georgia 25%" "kenya 25%" "uruguay 20%" "taiwan 30%" "lithuania 35%"; do
  set -- $x
  cp "$1.json" "$1-hi.json"
  $MS -i "$1-hi.json" -simplify "$2" keep-shapes -o "$1.json" format=geojson precision=0.0001 force
done
# Canada's boards are TopoJSON (other scripts read canada.json), kept with their object name; canada-hi.json holds the
# full detail, so this starts from it.
$MS -i canada-hi.json -simplify 4% keep-shapes -o canada.json format=topojson quantization=100000 force

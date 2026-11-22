#!/bin/sh
# Simplifies the most detailed borders so the map stays light enough to pan and zoom (mapshaper, topology-aware: shared
# edges stay shared, and keep-shapes keeps every small district). Run after the prep scripts that write these files
# (they write geoBoundaries' full detail), then rebuild with build_latam.py. Needs mapshaper (npm install mapshaper).
set -e
cd "$(dirname "$0")"
MS=${MAPSHAPER:-mapshaper}
for x in "india/ind_geo 12%" "costa_rica/cr_geo 10%" "south_africa/zaf_geo 25%" "georgia/geo_geo 25%" "kenya/ken_geo 25%" \
         "uruguay/ury_geo 20%" "taiwan/tw_geo 30%" "lithuania/ltu_geo 35%"; do
  set -- $x
  $MS -i "inputs/$1.geojson" -simplify "$2" keep-shapes -o "inputs/$1.geojson" precision=0.0001 force
done
# Canada's boards (TopoJSON; other scripts read it too, so it stays TopoJSON with its object name).
$MS -i ../docs/data/map/canada.json -simplify 4% keep-shapes -o ../docs/data/map/canada.json format=topojson quantization=100000 force

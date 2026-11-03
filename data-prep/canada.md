# Canadian school boards

`docs/data/canada.csv` and `docs/data/map/canada.json` are built in three steps. Steps 1 and 2 need
internet access; Statistics Canada's site refuses GitHub's servers, so the census subdivision
boundary file is copied to this repo's `statcan-csd-2021` release.

1. `python3 data-prep/build_canada.py WORK OUT` downloads Statistics Canada's low-income table
   (98-10-0103-01) and each province's board borders, and writes `OUT/canada.csv` and
   `OUT/canada_boards.geojson`. Each board's children 0–17 and children in low income (LIM-AT,
   2020 incomes) add up the census subdivisions inside its border; a subdivision split between
   boards is shared by land area (Wood Buffalo, Alberta, is shared by where people live instead).
   Nova Scotia, New Brunswick and the Northwest Territories have no published borders, so their
   boards are built from counties or regions; province- and territory-wide boards use the total.
   The map file is the geojson simplified with
   `mapshaper -simplify 4% keep-shapes -o canada.json format=topojson quantization=100000`.
2. `python3 data-prep/canada_youtube.py OUT/canada.csv canada_youtube.csv data-prep/inputs/canada_channels.csv`
   searches YouTube for each board's channel and counts videos whose titles show a board or
   committee meeting.
3. `python3 data-prep/finish_canada.py OUT/canada.csv canada_youtube.csv docs/data/canada.csv`
   joins the two and applies the hand-checked channel list in `data-prep/inputs/canada_channels.csv`
   (wrong channels the search found, such as US districts with the same name).

The inputs used for the site, as built in November 2026, are saved in `data-prep/inputs/canada/`.
Unlike the US data, Canada's figures aren't refreshed daily.

# Territory child poverty figures (2020 Census)

`docs/data/territories.csv` gets children ages 5–17 and children in poverty for Guam, the
Northern Mariana Islands, the U.S. Virgin Islands and American Samoa from each territory's
2020 Census Demographic and Housing Characteristics (DHC) summary file:

https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas/

The table is "Poverty status in 2019 by age by sex" (Guam PCT78, Northern Mariana Islands
PCT77, U.S. Virgin Islands PCT75, American Samoa PCT77). Its universe is people in households
for whom poverty status is determined (on Guam, not counting military housing units).
Children ages 5–17 are the "5 years", "6 to 11 years" and "12 to 17 years" rows for both sexes;
"in poverty" is the same rows under "Income in 2019 below poverty level".

The Census data API now needs a key, so the counts were read from the bulk summary files
(downloaded October 30, 2026), territory-wide record (logical record 1), and checked against
the Census press releases (Guam: 145,543 people, 29,408 below poverty; American Samoa: 48,506
and 26,480). The Virgin Islands are split by island (county records): St. Croix for the
St. Croix district, St. Thomas plus St. John for the other.

| Area | Children 5–17 | In poverty | Rate |
| --- | ---: | ---: | ---: |
| Guam | 29,567 | 8,853 | 29.9% |
| Northern Mariana Islands | 10,326 | 4,945 | 47.9% |
| U.S. Virgin Islands (all) | 12,486 | 3,920 | 31.4% |
| – St. Croix | 6,363 | 2,177 | 34.2% |
| – St. Thomas + St. John | 6,123 (5,700 + 423) | 1,743 (1,635 + 108) | 28.5% |
| American Samoa | 13,505 | 8,487 | 62.8% |

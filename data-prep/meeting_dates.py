"""Dates from meeting video titles, for "Latest meeting" and "Meetings by year".

Titles name their dates in many ways and languages: "15. April 2026", "Tuesday 29 September 2026",
"Séance publique du jeudi 26 mars 2026", "13.06.2025 - Seduta", "2024/12/23 - Συνεδρία", "8.6.21".
parse(title) returns (year, month, day) with month/day 0 when unknown, or None.
"""
import re

MONTHS = {}
for i, names in enumerate([
    "january jan januar janvier gennaio enero janeiro gener januari tammikuu janúar ιανουαρίου",
    "february feb februar février fevrier febbraio febrero fevereiro febrer februari helmikuu febrúar φεβρουαρίου",
    "march mar märz maerz mars marzo março marc maart maaliskuu ματίου μαρτίου",
    "april apr avril aprile abril abril huhtikuu apríl απριλίου",
    "may mai maggio mayo maio maig mei toukokuu maí μαΐου",
    "june jun juni juin giugno junio junho juny kesäkuu júní ιουνίου",
    "july jul juli juillet luglio julio julho juliol heinäkuu júlí ιουλίου",
    "august aug august août aout agosto agost augustus elokuu ágúst αυγούστου",
    "september sep sept september septembre settembre septiembre setembro setembre syyskuu σεπτεμβρίου",
    "october oct oktober octobre ottobre octubre outubro octubre lokakuu október οκτωβρίου",
    "november nov november novembre noviembre novembro novembre marraskuu nóvember νοεμβρίου",
    "december dec dezember desember décembre decembre dicembre diciembre dezembro desembre joulukuu desember δεκεμβρίου",
], start=1):
    for n in names.split():
        MONTHS.setdefault(n, i)
MON = "|".join(sorted(MONTHS, key=len, reverse=True))
ok = lambda y: 2000 <= y <= 2027


def parse(title):
    s = title.lower()
    # 15. april 2026 / 15 april, 2026 / 6th october 2026 / 26 mars 2026 / 26 de outubro de 2021
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th|er|º|ª)?\.?\s+(?:de\s+)?(" + MON + r")\.?,?\s+(?:de\s+)?(\d{4})\b", s)
    if m and ok(int(m.group(3))): return (int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    # april 15, 2026 / september 29th 2026
    m = re.search(r"\b(" + MON + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", s)
    if m and ok(int(m.group(3))): return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    # 2024/12/23, 2026-01-11
    m = re.search(r"\b(20\d\d)[./-](\d{1,2})[./-](\d{1,2})\b", s)
    if m and 1 <= int(m.group(2)) <= 12: return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # 13.06.2025, 12/08/2022, 8.6.21, 12.04.23 (day first, as nearly all these countries write it)
    m = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4}|\d{2})\b", s)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        d, mo = int(m.group(1)), int(m.group(2))
        if mo > 12 and d <= 12: d, mo = mo, d   # 12/25/2024, US style
        if ok(y) and 1 <= mo <= 12: return (y, mo, d)
    # november 2021 / maí 2024
    m = re.search(r"\b(" + MON + r")\s+(\d{4})\b", s)
    if m and ok(int(m.group(2))): return (int(m.group(2)), MONTHS[m.group(1)], 0)
    # a year on its own (e.g. "PY2024-2025 Public Meeting #17" gives the first year)
    m = re.search(r"\b(20\d\d)\b", s)
    if m and ok(int(m.group(1))): return (int(m.group(1)), 0, 0)
    return None


def summary(titles):
    """("2026-10-13", "2024:12; 2025:30; 2026:21") for a list of counted meeting titles: the latest date
    found and the number of distinct dated meetings per year (undated titles are left out)."""
    import datetime
    t = datetime.date.today(); now = (t.year, t.month, t.day)
    # Titles with a date in the future are typos (e.g. "2 december 2027"): leave them out.
    dates = {d for d in (parse(t) for t in titles) if d and (d[0], d[1] or 1, d[2] or 1) <= now}
    if not dates:
        return "", ""
    y, m, d = max(dates)
    latest = f"{y:04d}" + (f"-{m:02d}" if m else "") + (f"-{d:02d}" if m and d else "")
    per = {}
    for (yy, mm, dd) in dates:
        per[yy] = per.get(yy, 0) + 1
    return latest, "; ".join(f"{k}:{per[k]}" for k in sorted(per))

"""US school boards' meetings before 2025, from their YouTube channels.

CivicSearch (the site's US meeting counts) indexes meetings from January 2025. Each CivicSearch place links its latest
meeting video on YouTube; that video's channel (from YouTube's oEmbed endpoint) holds the board's older recordings.
The titles of each channel's videos and live streams were listed once (fetch round 68b, 28 November 2026, on the
GitHub runner: claude/world-fetch-2, fetch/out/c68/us_youtube_titles.json).

A title counts as a board meeting when it names the board (board, BOE, trustees, school committee) and a meeting
(meeting, session, workshop, hearing, retreat, or a livestream of the board). Its date comes from the title; a
recording in several parts, or posted twice, counts once per date. Titles with only a month and year count once per
title. Writes data-prep/inputs/us_youtube_meetings.json: {query_id: {"channel": url, "years": {year: meetings}}},
which build_national.py reads for the years before CivicSearch's.

Usage: python3 data-prep/prep_us_youtube_history.py TITLES_JSON
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "us_youtube_meetings.json")

BOARD = re.compile(r"\bboard\b|\bboe\b|b\.o\.e|\btrustees?\b|school committee|\bbog\b", re.I)
MEETING = re.compile(r"meeting|\bmtg\b|session|workshop|hearing|retreat|live ?stream|\bbusiness\b|regular|special|called", re.I)
NOT = re.compile(r"graduat|commencement|hall of fame|football|basketball|baseball|softball|soccer|volleyball|wrestling|concert|"
                 r"choir|band\b|senior night|homecoming|teacher of the (year|month)|student of the|spotlight|award|ceremony|"
                 r"promo|trailer|highlights?\b|announcement|recap|interview|podcast|candidate|forum|town hall|open house", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"


def year4(y):
    y = int(y)
    return y + 2000 if y < 100 else y


def date_of(t):
    """(year, month, day) from a title (day 0 when only the month is given), or None."""
    s = t.lower()
    m = re.search(r"\b(20\d\d)[-./](\d{1,2})[-./](\d{1,2})\b", s)                      # 2024-01-15
    if m: return int(m[1]), int(m[2]), int(m[3])
    m = re.search(MON + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d|'?\d\d)\b", s)       # January 15, 2024
    if m: return year4(m[3].lstrip("'")), MONTHS[m[1][:3]], int(m[2])
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+" + MON + r",?\s+(20\d\d)\b", s)      # 15 January 2024
    if m: return int(m[3]), MONTHS[m[2][:3]], int(m[1])
    m = re.search(r"(?<![\d/.-])(\d{1,2})[./-](\d{1,2})[./-](20\d\d|\d\d)(?![\d/.-])", s)  # 1/15/24, 01-15-2024
    if m and 1 <= int(m[1]) <= 12 and 1 <= int(m[2]) <= 31: return year4(m[3]), int(m[1]), int(m[2])
    m = re.search(r"(?<!\d)(\d{1,2})\s(\d{1,2})\s(\d\d)(?!\d)", s)                       # 7 26 21
    if m and 1 <= int(m[1]) <= 12 and 1 <= int(m[2]) <= 31: return year4(m[3]), int(m[1]), int(m[2])
    m = re.search(r"(?<!\d)(\d{1,2})(\d{2})(\d{2})(?!\d)", s)                             # 012624
    if m and 1 <= int(m[1]) <= 12 and 1 <= int(m[2]) <= 31 and 10 <= int(m[3]) <= 30: return year4(m[3]), int(m[1]), int(m[2])
    m = re.search(MON + r",?\s+(20\d\d)\b", s)                                            # January 2024
    if m: return int(m[2]), MONTHS[m[1][:3]], 0
    return None


def is_meeting(t):
    return bool(BOARD.search(t) and MEETING.search(t) and not NOT.search(t))


def count(titles):
    dates, undated_month = set(), {}
    for t in titles:
        if not is_meeting(t): continue
        d = date_of(t)
        if not d or not (2005 <= d[0] <= 2026) or not (1 <= d[1] <= 12): continue
        if d[2]: dates.add(d)
        else: undated_month[t] = d[0]
    years = {}
    for y, _, _ in dates: years[y] = years.get(y, 0) + 1
    for y in undated_month.values(): years[y] = years.get(y, 0) + 1
    return {str(y): n for y, n in sorted(years.items())}


def main(src):
    d = json.load(open(src, encoding="utf-8"))
    counts = {ch: count([x[0] for x in items]) for ch, items in d["channels"].items()}
    out = {q: {"channel": ch, "years": counts.get(ch, {})} for q, ch in d["places"].items() if ch}
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
    print(len(out), "places;", sum(1 for v in out.values() if any(int(y) < 2025 for y in v["years"])), "with meetings before 2025")


if __name__ == "__main__":
    main(sys.argv[1])

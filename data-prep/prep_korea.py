"""Turns the South Korea downloads (made on GitHub's runner) into the small inputs build_latam.south_korea() reads
(data-prep/inputs/south_korea/).

- kor_geo.geojson: the 17 metropolitan cities and provinces, from geoBoundaries gbOpen KOR ADM1 (simplified).
- kor_data.json, per province or city:
  recipients, rate: Ministry of Health and Welfare, "2025년 국민기초생활보장 수급자 현황" (2026), Table 1 (recipients of the
    National Basic Livelihood Security system, households and persons, with facility recipients) and the recipient rate
    by province (수급률: recipients over the resident-registration population);
  pop: recipients over the rate (both MOHW's), so approximate;
  pupils: Ministry of Education / KEDI, "연도별 시도별 현황" (education statistics by province, KESS, updated 1 October 2026),
    sheet 01 (개황): pupils in elementary, middle and high schools, latest year (all establishment types; no public split);
  meetings: the council's YouTube channel (fetch/kr_yt.py): its education committee (교육위원회) where at least three of
    its meetings are posted, otherwise its plenary sittings (본회의), each counted once per session and sitting number
    (clips of a member's speech from a sitting count for that sitting).
Usage: python3 data-prep/prep_korea.py MOHW_PDF KR_MEET_JSON GEODIR [PUPILS_XLSX]
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "south_korea")
# Korean name, short name in MOHW's tables, English (geoBoundaries), kind
P = [("서울특별시", "서 울", "Seoul", "Special city"), ("부산광역시", "부 산", "Busan", "Metropolitan city"), ("대구광역시", "대 구", "Daegu", "Metropolitan city"),
     ("인천광역시", "인 천", "Incheon", "Metropolitan city"), ("광주광역시", "광 주", "Gwangju", "Metropolitan city"), ("대전광역시", "대 전", "Daejeon", "Metropolitan city"),
     ("울산광역시", "울 산", "Ulsan", "Metropolitan city"), ("세종특별자치시", "세 종", "Sejong", "Special self-governing city"), ("경기도", "경 기", "Gyeonggi", "Province"),
     ("강원특별자치도", "강 원", "Gangwon", "Special self-governing province"), ("충청북도", "충 북", "North Chungcheong", "Province"), ("충청남도", "충 남", "South Chungcheong", "Province"),
     ("전북특별자치도", "전 북", "North Jeolla", "Special self-governing province"), ("전라남도", "전 남", "South Jeolla", "Province"), ("경상북도", "경 북", "North Gyeongsang", "Province"),
     ("경상남도", "경 남", "South Gyeongsang", "Province"), ("제주특별자치도", "제 주", "Jeju", "Special self-governing province")]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def meetings(videos):
    """(n, type, titles): distinct (session 회, sitting 차) of the education committee, or else of plenary sittings."""
    def keyed(pat):
        keys, keep = set(), []
        for t in videos:
            # Clips of one member's speech or question from a sitting ("5분자유발언", "도정질문") count for that sitting, as in
            # Brazil; promotional videos, site visits and forums don't.
            if not re.search(pat, t) or re.search(r"현장방문|현장점검|소개|토론회|축제|하이라이트|홍보|인터뷰|쇼츠|#shorts|예고|브이로그", t, re.I): continue
            s = re.search(r"제\s*(\d+)\s*회", t); c = re.search(r"제\s*(\d+)\s*차", t); d = re.search(r"(20\d\d)[-.]\s?(\d{1,2})[-.]\s?(\d{1,2})", t)
            if not (s or d): continue
            keys.add((s.group(1) if s else "", c.group(1) if c else "", d.group(0) if d and not c else "")); keep.append(t)
        return keys, keep
    k, t = keyed(r"교육위원회")
    if len(k) >= 3: return len(k), "Council education committee (stand-in)", t
    k, t = keyed(r"본회의")
    return (len(k), "Council plenary sittings (stand-in)", t) if k else (0, "", [])


def main(pdf, meet, geo, pupils=None):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    t1 = txt[txt.index("<표 1> 수급자 현황 - 수급자 종류별, 시도별", 20000):]
    rows = {}
    for line in t1.splitlines()[:60]:
        m = re.match(r"\s*([가-힣] [가-힣])\s+([\d,]+)\s+([\d,]+)", line)
        if m: rows[m.group(1)] = (int(m.group(2).replace(",", "")), int(m.group(3).replace(",", "")))
    i = txt.index("<지역별 국민기초생활보장 수급률>")
    nums = [float(x) for x in re.findall(r"\d+\.\d", txt[i:i + 1500])[:18]]   # 전국, then the 17 in MOHW's order
    rate = dict(zip([p[1] for p in P], nums[1:]))
    mt = json.load(open(meet, encoding="utf-8"))
    pup, pyear = {}, None
    if pupils:
        import openpyxl
        ws = openpyxl.load_workbook(pupils, read_only=True)["01"]
        rows01 = [r for r in ws.iter_rows(min_row=4, values_only=True) if r[0]]
        pyear = max(int(r[0]) for r in rows01)
        for r in rows01:
            if int(r[0]) == pyear and r[2] in ("초등학교", "중학교", "고등학교"):
                pup[r[1]] = pup.get(r[1], 0) + int(r[7] or 0)
    g = {f["properties"]["shapeName"]: f for f in json.load(open(os.path.join(geo, "geoBoundaries-KOR-ADM1_simplified.geojson"), encoding="utf-8"))["features"]}
    data, feats = {}, []
    for i, (ko, short, en, kind) in enumerate(P):
        hh, persons = rows[short]
        n, typ, titles = meetings((mt.get(ko) or {}).get("videos", []))
        data[ko] = {"code": f"{i + 1:02d}", "en": en, "kind": kind, "households": hh, "recipients": persons, "rate": rate[short],
                    "pop": round(persons / rate[short] * 100), "pupils": pup.get(short.replace(" ", "")), "pupils_year": pyear, "meetings": {"n": n, "type": typ, "source": (mt.get(ko) or {}).get("url", "") if n else "", "titles": titles}}
        f = g[en]
        feats.append({"type": "Feature", "properties": {"id": f"KOR-{i + 1:02d}", "NAME": en}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "kor_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "kor_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for ko, x in data.items(): print(x["en"], x["recipients"], x["rate"], x["pop"], x["pupils"], x["meetings"]["n"], x["meetings"]["type"])
    print("pop", sum(x["pop"] for x in data.values()))


def history(pupils):
    """Adds every year of pupils (elementary, middle and high schools) to kor_data.json, from the same KESS file's sheet 01."""
    import openpyxl
    ws = openpyxl.load_workbook(pupils, read_only=True)["01"]
    by = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] and r[2] in ("초등학교", "중학교", "고등학교"):
            d = by.setdefault(r[1], {}); d[str(int(r[0]))] = d.get(str(int(r[0])), 0) + int(r[7] or 0)
    f = os.path.join(OUT, "kor_data.json")
    data = json.load(open(f, encoding="utf-8"))
    for ko, x in data.items():
        short = next(p[1] for p in P if p[0] == ko).replace(" ", "")
        x["pupil_years"] = dict(sorted(by.get(short, {}).items()))
    json.dump(data, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ys = sorted({y for x in data.values() for y in x["pupil_years"]})
    print("Korea pupils by year:", ys[:1], "-", ys[-1:], sum(1 for x in data.values() if x["pupil_years"]), "provinces")


if __name__ == "__main__":
    if sys.argv[1] == "--history": history(sys.argv[2]); sys.exit()   # prep_korea.py --history KESS.xlsx
    main(*sys.argv[1:])

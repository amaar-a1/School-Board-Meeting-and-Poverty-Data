"""South Korea: each metropolitan or provincial council's YouTube channel; its plenary sessions (본회의) and education
committee (교육위원회) meetings. Writes OUT/kr_meet.json: {council: {"channel", "url", "videos": [titles]}}"""
import json, os, re, subprocess, sys, time
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
C = [("서울특별시", "서울", True), ("부산광역시", "부산", True), ("대구광역시", "대구", True), ("인천광역시", "인천", True), ("광주광역시", "광주", True),
     ("대전광역시", "대전", True), ("울산광역시", "울산", True), ("세종특별자치시", "세종", True), ("경기도", "경기", False), ("강원특별자치도", "강원", False),
     ("충청북도", "충북", False), ("충청남도", "충남", False), ("전북특별자치도", "전북", False), ("전라남도", "전남", False), ("경상북도", "경북", False),
     ("경상남도", "경남", False), ("제주특별자치도", "제주", False)]
LONG = {"충북": "충청북도", "충남": "충청남도", "전북": "전라북도|전북특별자치도", "전남": "전라남도", "경북": "경상북도", "경남": "경상남도"}
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=900)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)
def ok(ch, short, metro):
    if "의회" not in ch or re.search(r"의원|당|위원장|tv조선|뉴스|방송", ch, re.I): return False
    if not (short in ch or re.search(LONG.get(short, "^$"), ch)): return False
    if re.search(r"[가-힣]{1,4}(구|군)의회", ch): return False          # district and county councils
    if not metro and re.search(r"[가-힣]{1,4}시의회", ch): return False   # city councils inside a province
    return True
res = {}
for full, short, metro in C:
    rec = {"channel": "", "url": "", "videos": [], "cands": {}}
    try:
        for q in (f"{full}의회 교육위원회", f"{full}의회 본회의", f"{short} 의회 생중계"):
            for e in yt(f"ytsearch20:{q}").get("entries") or []:
                if e.get("channel_url") and e.get("channel"): rec["cands"][e["channel_url"]] = e["channel"]
            time.sleep(1.5)
        good = [(u, ch) for u, ch in rec["cands"].items() if ok(ch, short, metro)]
        if good:
            u, ch = good[0]; vids = []
            for tab in ("/videos", "/streams"):
                try: vids += [v.get("title") or "" for v in yt(u + tab).get("entries") or []]
                except RuntimeError: pass
                time.sleep(1)
            rec.update(channel=ch, url=u, videos=vids)
    except Exception as e:
        rec["err"] = str(e)[:200]
    res[full] = rec; print(full, rec["channel"], len(rec["videos"]), flush=True)
    json.dump(res, open(f"{OUT}/kr_meet.json", "w"), ensure_ascii=False)

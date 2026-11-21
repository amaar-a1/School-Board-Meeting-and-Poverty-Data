"""Argentina, round 2: each provincial legislature's YouTube channel(s), with the recordings of its plenary sittings and
of its education committee, and a date for each (from the title, else the video's upload date).
Writes OUT/ar_meet.json: {province: {"channels": [...], "videos": [{title, url, date, kind}]}}."""
import json, os, re, subprocess, sys, time
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
CH = {"Ciudad Autónoma de Buenos Aires": ["UC6AHvTa7a-iAeZmcjnagPVQ"], "Buenos Aires": ["UCQ75bCTMGKHlnGCJre2VDxQ", "UCr32BL1HMt5bPPGM0CuDrAA"],
      "San Luis": ["UCm2Wryf2GiBXWEjUHUJhEqw"], "Río Negro": ["UCVpVCcU35rfgAb4etaDOqQg"], "Catamarca": ["UC2HnM2bfuyDnqg1BTeBd8Eg"],
      "Santa Fe": ["UCucnisxBQzhz8J2xDDmHT8g", "UCg0Jjl-JBsFE8O2jwmDz6kA"], "Chubut": ["UCZ8NnJma59nCU9Ijcw2p3pg"],
      "Córdoba": ["UCuBF5oa2wSvwj7EYHK2EOKQ"], "Neuquén": ["UCe9zoG87bDXXNpd_7dRVWtg"], "Corrientes": ["UCaKzoDdrgujAXRX83vAukqw"],
      "Santa Cruz": ["UCNfsNMoyLSpczRgGbWyCTmA"], "Jujuy": ["UC4DBq_mP12clM1yNG6dseAQ"], "Entre Ríos": ["UC_oaQGOSpuSk8huuosmQ_pQ", "UCj0dNRrNFOyz5g-LoUEG8Mg"],
      "La Rioja": ["UCsnyCtaCQrOF9DOXgVQsctw"], "Salta": ["UCsnG0KeevsvKUdMqZmoqs9A", "UCtAVTuWAKFw8tUrcjHz57Yw"], "San Juan": ["UCdaBPf51idsbBbJ4yPmlucQ"]}
MISSING = {"Chaco": "Chaco", "Formosa": "Formosa", "La Pampa": "Pampa", "Mendoza": "Mendoza", "Misiones": "Misiones",
           "Santiago del Estero": "Santiago", "Tierra del Fuego": "Fuego", "Tucumán": "Tucum"}
def yt(*a, timeout=900):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", *a], capture_output=True, text=True, timeout=timeout)
    if r.returncode and not r.stdout: raise RuntimeError(r.stderr.strip()[-300:])
    return r.stdout
log = open(f"{OUT}/ar_meet_log.txt", "w")
for p, key in MISSING.items():
    found = []
    for q in (f"Legislatura de {p} sesión ordinaria", f"Cámara de Diputados de {p} sesión", f"Legislatura {p} comisión de educación"):
        try:
            for e in json.loads(yt("--flat-playlist", "-J", f"ytsearch25:{q}")).get("entries") or []:
                c = e.get("channel") or ""
                if re.search(r"legislatura|c[aá]mara|diputad|senado|poder legislativo", c, re.I) and re.search(key, c, re.I):
                    cid = (e.get("channel_url") or "").rsplit("/", 1)[-1]
                    if cid and cid not in found: found.append(cid); print(p, "->", c, cid, file=log, flush=True)
        except Exception as ex: print(p, q, "ERR", ex, file=log, flush=True)
        time.sleep(2)
    CH[p] = found
SES = re.compile(r"\bsesi[oó]n\b.*\b(ordinaria|extraordinaria|especial|preparatoria|inaugural|conjunta|de pr[oó]rroga|virtual|legislativa)|\b(ordinaria|extraordinaria|especial|preparatoria|inaugural)\b.*\bsesi[oó]n\b|^sesi[oó]n\b|\bsesi[oó]n\s+(n[°ºo]|\d)", re.I)
EDU = re.compile(r"comisi[oó]n(es)?\b.*educaci|educaci.*\bcomisi[oó]n|comisiones permanentes\s*\|\s*educaci|reuni[oó]n ordinaria de comisiones\s*\|\s*educaci", re.I)
SKIP = re.compile(r"juvenil|estudiantil|infantil|simulad|voz joven|concejo deliberante|podcast|resumen|enterate|himno|cant[oó]|entrevista|\bnota\b|an[aá]lisis|conferencia de prensa|homenaje a|inter?venci[oó]n|^dip\.|^sen\.|^diputad[oa] |^senador|^legislador", re.I)
MON = {m: i + 1 for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"])}
MON["setiembre"] = 9
MONABB = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AGO": 8, "SEP": 9, "SET": 9, "OCT": 10, "NOV": 11, "DIC": 12}
def tdate(t):
    m = re.search(r"\b(\d{1,2})\s+(?:de\s+)?([a-záé]+)\s+(?:de\s+|del\s+)?(\d{4})", t, re.I)
    if m and m.group(2).lower() in MON: return f"{int(m.group(3)):04d}-{MON[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(\d{1,2})[-/. ](\d{1,2})[-/. ](\d{4}|\d{2})\b", t)
    if m:
        y = int(m.group(3)); y = y + 2000 if y < 100 else y
        if 1 <= int(m.group(2)) <= 12: return f"{y:04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(20\d\d)-(\d\d)-(\d\d)\b", t)
    if m: return m.group(0)
    m = re.search(r"\b(\d{1,2})([A-Z]{3})(20\d\d)\b", t)
    if m and m.group(2) in MONABB: return f"{m.group(3)}-{MONABB[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None
res = {}
for p, cids in CH.items():
    vids = []
    for cid in cids:
        for tab in ("/videos", "/streams"):
            try:
                for e in json.loads(yt("--flat-playlist", "-J", f"https://www.youtube.com/channel/{cid}{tab}")).get("entries") or []:
                    t = e.get("title") or ""
                    kind = "edu" if EDU.search(t) else "sitting" if SES.search(t) else None
                    if kind and not SKIP.search(t.strip()): vids.append({"title": t, "url": e.get("url"), "id": e.get("id"), "kind": kind, "date": tdate(t), "channel": cid})
            except Exception as ex: print(p, cid, tab, "ERR", ex, file=log, flush=True)
            time.sleep(1)
    # upload dates for the newest undated ones (playlists list newest first)
    need = [v for v in vids if not v["date"]][:200]
    for v in need:
        try: v["date"] = (lambda s: f"{s[:4]}-{s[4:6]}-{s[6:8]}" if re.fullmatch(r"\d{8}", s) else None)(yt("--skip-download", "--print", "upload_date", f"https://www.youtube.com/watch?v={v['id']}", timeout=120).strip()); v["date_from"] = "upload"
        except Exception as ex: print(p, v["id"], "ERR", str(ex)[:120], file=log, flush=True)
        time.sleep(0.5)
    res[p] = {"channels": cids, "videos": vids}
    print(p, len(cids), "channels", len(vids), "videos", sum(1 for v in vids if v["date"]), "dated", file=log, flush=True)
    json.dump(res, open(f"{OUT}/ar_meet.json", "w"), ensure_ascii=False)

"""Find each island's legislature on YouTube and list its videos (stand-in for school board meetings).

No island has an elected school board: a government ministry runs the schools and doesn't meet in
public. As for Saint-Pierre-et-Miquelon, the stand-in is the elected legislature (parliament, house of
assembly, territorial council), whose sittings pass the education budget and laws.
For each island: search YouTube with its legislature's name (QUERIES), keep every channel found with
its hit count and sample titles, pick the channel whose name looks official (LEGIS words) with the
most hits, and save all its video titles. build_islands.py counts sittings from the titles.
Usage: python3 islands_youtube.py OUTDIR
"""
import json, os, re, subprocess, sys, time

QUERIES = {
    "AIA": "Anguilla House of Assembly sitting", "ATG": "Antigua and Barbuda House of Representatives sitting",
    "ABW": "Staten van Aruba openbare vergadering", "BHS": "Bahamas House of Assembly sitting",
    "BHR": "Bahrain Council of Representatives session", "BRB": "Barbados House of Assembly sitting",
    "BMU": "Bermuda House of Assembly sitting", "VGB": "Virgin Islands House of Assembly sitting",
    "CPV": "Assembleia Nacional Cabo Verde sessão plenária", "CYM": "Cayman Islands Parliament sitting",
    "COM": "Assemblée de l'Union des Comores séance plénière", "COK": "Cook Islands Parliament sitting",
    "CUW": "Staten van Curaçao openbare vergadering", "CYP": "Βουλή των Αντιπροσώπων ολομέλεια συνεδρίαση",
    "DMA": "Dominica House of Assembly sitting", "FLK": "Falkland Islands Legislative Assembly meeting",
    "FRO": "Løgtingið tingfundur", "FSM": "FSM Congress session", "FJI": "Parliament of Fiji sitting",
    "PYF": "Assemblée de la Polynésie française séance", "GRL": "Inatsisartut ataatsimiinneq",
    "GRD": "Grenada House of Representatives sitting", "GGY": "States of Guernsey meeting",
    "IMN": "Tynwald sitting", "JAM": "Jamaica House of Representatives sitting", "JEY": "States Assembly Jersey sitting",
    "KIR": "Kiribati Maneaba ni Maungatabu parliament", "MDV": "People's Majlis sitting Maldives",
    "MLT": "Parlament ta' Malta seduta plenarja", "MHL": "Nitijela session Marshall Islands",
    "MUS": "National Assembly Mauritius sitting", "MSR": "Montserrat Legislative Assembly sitting",
    "NRU": "Parliament of Nauru sitting", "NCL": "Congrès de la Nouvelle-Calédonie séance publique",
    "NIU": "Niue Assembly meeting", "NFK": "Norfolk Island Regional Council meeting",
    "PLW": "Olbiil Era Kelulau Palau session", "SHN": "St Helena Legislative Council meeting",
    "KNA": "St Kitts and Nevis National Assembly sitting", "LCA": "Saint Lucia House of Assembly sitting",
    "VCT": "St Vincent and the Grenadines House of Assembly sitting", "BLM": "Conseil territorial Saint-Barthélemy séance",
    "MAF": "Conseil territorial Saint-Martin séance", "WSM": "Samoa Parliament sitting",
    "SYC": "National Assembly Seychelles sitting", "SGP": "Singapore Parliament sitting",
    "SXM": "Parliament of Sint Maarten public meeting", "SLB": "Solomon Islands National Parliament sitting",
    "STP": "Assembleia Nacional São Tomé e Príncipe sessão plenária", "TON": "Legislative Assembly of Tonga sitting",
    "TTO": "Parliament of Trinidad and Tobago House of Representatives sitting", "TCA": "Turks and Caicos House of Assembly sitting",
    "TUV": "Tuvalu Parliament sitting", "VUT": "Parliament of Vanuatu sitting", "WLF": "Assemblée territoriale Wallis et Futuna séance",
}
# Swiss cantonal parliaments and the European microstates' parliaments (same method).
EUROPE = {
    "CH-ZH": "Kantonsrat Zürich Sitzung", "CH-BE": "Grosser Rat Bern Session", "CH-LU": "Kantonsrat Luzern Session",
    "CH-UR": "Landrat Uri Sitzung", "CH-SZ": "Kantonsrat Schwyz Sitzung", "CH-OW": "Kantonsrat Obwalden Sitzung",
    "CH-NW": "Landrat Nidwalden Sitzung", "CH-GL": "Landrat Glarus Sitzung", "CH-ZG": "Kantonsrat Zug Sitzung",
    "CH-FR": "Grand Conseil Fribourg session", "CH-SO": "Kantonsrat Solothurn Session", "CH-BS": "Grosser Rat Basel-Stadt Sitzung",
    "CH-BL": "Landrat Basel-Landschaft Sitzung", "CH-SH": "Kantonsrat Schaffhausen Sitzung", "CH-AR": "Kantonsrat Appenzell Ausserrhoden Sitzung",
    "CH-AI": "Grosser Rat Appenzell Innerrhoden Session", "CH-SG": "Kantonsrat St. Gallen Session", "CH-GR": "Grosser Rat Graubünden Session",
    "CH-AG": "Grosser Rat Aargau Sitzung", "CH-TG": "Grosser Rat Thurgau Sitzung", "CH-TI": "Gran Consiglio ticinese seduta",
    "CH-VD": "Grand Conseil vaudois séance", "CH-VS": "Grand Conseil valaisan session", "CH-NE": "Grand Conseil neuchâtelois session",
    "CH-GE": "Grand Conseil Genève séance", "CH-JU": "Parlement jurassien séance",
    "LUX": "Chambre des Députés Luxembourg séance publique", "LIE": "Landtag Liechtenstein Sitzung", "MCO": "Conseil National Monaco séance publique",
    "AND": "Consell General Andorra sessió", "SMR": "Consiglio Grande e Generale San Marino seduta",
}
LEGIS = re.compile(LEGIS = re.compile(r"parliament|parlament|assembly|assembl[ée]e|assembleia|house of|legislat|congr[eè]s|congress|staten|tynwald|"
                   r"states|majlis|nitijela|fono|inatsisartut|l[øo]gting|council|conseil|βουλ|senate|maneaba|kelulau|government|gov|ministry|nation|kantonsrat|grosser rat|grand conseil|landrat|gran consiglio|landtag|consell|consiglio|chambre|kanton|canton", re.I)


def ytdlp(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=900)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)


def main(outdir, which="islands"):
    os.makedirs(outdir, exist_ok=True)
    found, titles = {}, {}
    for iso, q in (EUROPE if which == "europe" else QUERIES).items():
        chans = {}
        try:
            for e in ytdlp(f"ytsearch25:{q}").get("entries") or []:
                if e.get("channel_url"):
                    c = chans.setdefault(e["channel_url"], {"name": e.get("channel") or "", "hits": 0, "titles": []})
                    c["hits"] += 1; c["titles"].append(e.get("title") or "")
        except Exception as ex:
            found[iso] = {"error": str(ex)[:200]}
            if "Sign in to confirm" in str(ex): break
            continue
        ranked = sorted(chans.items(), key=lambda x: (-bool(LEGIS.search(x[1]["name"])), -x[1]["hits"]))
        found[iso] = {"query": q, "channels": [{"url": u, **c} for u, c in ranked[:8]]}
        if ranked and ranked[0][0] not in titles:
            url = ranked[0][0]; vids = []
            for tab in ("/videos", "/streams"):
                try: vids += [v.get("title") or "" for v in ytdlp(url + tab).get("entries") or []]
                except RuntimeError: pass
                time.sleep(1)
            titles[url] = vids
        print(iso, "->", ranked[0][1]["name"] if ranked else None, flush=True)
        json.dump(found, open(f"{outdir}/islands_channels.json", "w"), ensure_ascii=False)
        json.dump(titles, open(f"{outdir}/islands_titles.json", "w"), ensure_ascii=False)
        time.sleep(1.5)


if __name__ == "__main__":
    main(sys.argv[1], *(sys.argv[2:3]))

# Temporary: details for untitled Guam streams, channel playlists, and NCES enrollment for Guam/American Samoa.
import json, subprocess, sys, urllib.request
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"], check=True)
out = {"guam_details": [], "nces": {}}
for vid in "AVE9W908OhQ ZSwsLU1NgK8 p3TgbwvovEY 4Bj6-_C4z00 WMHDxY9LmjQ aqml99ajztE FF_2Nb9s1E8 9mEQ-8nVsKo uDBNErn7YpQ AJvAncTsldc Kr1dnIF2054 bucj3kX82kQ br3JAL6f_mA qctPmnzy0wI bYDmYlM4u1E QXP-vlUYl-w kw5aEcChwfE T2spj89YR3s xks_Nh1hJJ0 y5EO1_MLqWU PPWiS4SX8MA U0QoHiql6Pc OeBlZUpJ-GQ wvwFt_51kMU 2q34-iCqw2E 7PTC6gGg5ic 22v6FPwwD7E h9GulRC6SWU".split():
    r = subprocess.run(["yt-dlp", "--skip-download", "--dump-json", "--no-warnings", f"https://www.youtube.com/watch?v={vid}"],
                       capture_output=True, text=True, timeout=300)
    try:
        d = json.loads(r.stdout)
        out["guam_details"].append({k: d.get(k) for k in ("id", "title", "upload_date", "release_timestamp", "duration", "description")})
    except ValueError:
        out["guam_details"].append({"id": vid, "error": r.stderr[-300:]})
def flat(target):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", target], capture_output=True, text=True, timeout=600)
    return [{k: json.loads(l).get(k) for k in ("title", "id", "url")} for l in r.stdout.splitlines() if l.startswith("{")]
out["cnmi_playlists"] = flat("https://www.youtube.com/channel/UCkbpGWkvnelMHKwyFGpwf0w/playlists")
out["guam_playlists"] = flat("https://www.youtube.com/@guamdepartmentofeducation5142/playlists")
for year in (2019, 2020, 2021, 2022):
    for fips in (66, 60):
        try:
            with urllib.request.urlopen(f"https://educationdata.urban.org/api/v1/school-districts/ccd/directory/{year}/?fips={fips}", timeout=120) as r:
                res = json.load(r)["results"]
            out["nces"][f"{year}_{fips}"] = [{k: x.get(k) for k in ("leaid", "lea_name", "enrollment", "number_of_schools")} for x in res]
        except Exception as e:
            out["nces"][f"{year}_{fips}"] = str(e)
json.dump(out, open("fetch/out/territory_check.json", "w"), indent=1)

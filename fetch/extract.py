# Temporary: list territory school board meeting videos.
import json, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"], check=True)
out = {}
def ytlist(key, target):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", target],
                       capture_output=True, text=True, timeout=900)
    items = []
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line)
            items.append({k: d.get(k) for k in ("title", "id", "upload_date", "timestamp", "duration", "channel", "channel_id", "url")})
        except ValueError:
            pass
    out[key] = {"target": target, "count": len(items), "items": items, "stderr": r.stderr[-1500:]}
ytlist("cnmi_videos", "https://www.youtube.com/channel/UCkbpGWkvnelMHKwyFGpwf0w/videos")
ytlist("cnmi_streams", "https://www.youtube.com/channel/UCkbpGWkvnelMHKwyFGpwf0w/streams")
ytlist("viga_videos", "https://www.youtube.com/channel/UCUeosYkcAS4HVKSfbLNR0FA/videos")
ytlist("viga_streams", "https://www.youtube.com/channel/UCUeosYkcAS4HVKSfbLNR0FA/streams")
ytlist("search_vibe", "ytsearch60:VIBE Virgin Islands Board of Education board meeting St. Thomas St. Croix")
ytlist("search_asboe", "ytsearch40:ASDOE Board of Education meeting Pago Pago")
json.dump(out, open("fetch/out/territory_videos.json", "w"), indent=1)

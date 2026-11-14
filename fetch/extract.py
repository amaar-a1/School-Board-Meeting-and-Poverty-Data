# Temporary: read the Borgen Project article on education in the Pitcairn Islands.
import os, re, html, urllib.request
OUT = "fetch/out/pcn2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
try:
    t = urllib.request.urlopen(urllib.request.Request("https://borgenproject.org/education-in-the-pitcairn-islands/", headers=UA), timeout=60).read().decode("utf-8", "replace")
    date = re.findall(r'"datePublished":"([^"]+)"|article:published_time" content="([^"]+)"', t)
    body = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", t))))
    i = body.find("Pitcairn"); log.write(f"date {date[:2]}\n{body[max(0,i-200):i+6000]}\n")
except Exception as e: log.write(f"ERR {e}\n")
log.close()

# Round 44: Czechia: retry the municipalities whose YouTube search failed in round 43 (two shards, slower pace).
import os, subprocess, sys, time
OUT = "fetch/out/c44"; os.makedirs(OUT, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "NORDIC_DEADLINE": str(time.time() + 4.5 * 3600)}
ps = [subprocess.Popen([sys.executable, "fetch/nyt.py", f"{OUT}/CZ_{k}of2", f"CZ:{k}/2"], env=env, stdout=open(f"{OUT}/log_{k}.txt", "w"), stderr=subprocess.STDOUT) for k in range(2)]
for p in ps: p.wait()

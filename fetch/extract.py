# Round 43: council meetings on YouTube for Czechia (six shards, biggest towns first), Rwanda and Sri Lanka.
import os, subprocess, sys, time
OUT = "fetch/out/c43"; os.makedirs(OUT, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "NORDIC_DEADLINE": str(time.time() + 5.0 * 3600)}
jobs = [["RW", "LK"]] + [[f"CZ:{k}/6"] for k in range(6)]
tag = lambda j: "_".join(j).replace(":", "_").replace("/", "of")
ps = [subprocess.Popen([sys.executable, "fetch/nyt.py", f"{OUT}/{tag(j)}", *j], env=env, stdout=open(f"{OUT}/log_{tag(j)}.txt", "w"), stderr=subprocess.STDOUT) for j in jobs]
for p in ps: p.wait()

# Round 23: India: zila parishad channels on YouTube (three shards in parallel, stopping in time to save).
import os, subprocess, sys
OUT = "fetch/out/in23"; os.makedirs(OUT, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "IN_SECONDS": str(4.6 * 3600)}
ps = [subprocess.Popen([sys.executable, "fetch/in_yt.py", OUT, f"{k}/3"], env=env, stdout=open(f"{OUT}/log_{k}.txt", "w"), stderr=subprocess.STDOUT) for k in range(3)]
for p in ps: p.wait()

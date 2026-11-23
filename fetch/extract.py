# Round 33: council meetings on YouTube for Malaysia, Indonesia (three shards) and Paraguay, stopping in time to save.
import os, subprocess, sys, time
OUT = "fetch/out/c33"; os.makedirs(OUT, exist_ok=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "NORDIC_DEADLINE": str(time.time() + 4.8 * 3600)}
jobs = [["MY"], ["PY"], ["ID:0/3"], ["ID:1/3"], ["ID:2/3"]]
ps = [subprocess.Popen([sys.executable, "fetch/nyt.py", f"{OUT}/{'_'.join(j).replace(':', '_').replace('/', 'of')}", *j], env=env,
                       stdout=open(f"{OUT}/log_{'_'.join(j).replace(':', '_').replace('/', 'of')}.txt", "w"), stderr=subprocess.STDOUT) for j in jobs]
for p in ps: p.wait()

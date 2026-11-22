# Round 22 (user-authorized): India: UDISE+ district enrolment from the public dashboard's own API (open-services, with
# the client header its page sends): academic years, national state-wise, then district-wise for each state. Paced.
import os, json, urllib.request, time
OUT = "fetch/out/in22"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
B = "https://api.udiseplus.gov.in/open-services/v1.1/"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)",
     "Authorization": "Bearer df;lkjz8lke4lk345kljsdfkjdfgkljsf08994a/sdfljsdf879w4ra/sdflksdflksdf", "Identity": "test",
     "Origin": "https://dashboard.udiseplus.gov.in", "Referer": "https://dashboard.udiseplus.gov.in/"}
def call(n, path, body=None):
    try:
        req = urllib.request.Request(B + path, data=json.dumps(body).encode() if body is not None else None, headers=H)
        b = urllib.request.urlopen(req, timeout=120).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {path} {json.dumps(body)}\n   {b[:500]!r}\n")
    except Exception as e: log.write(f"== {n} ERR {e} {path} {json.dumps(body)}\n")
    log.flush(); time.sleep(3)
call("years.json", "acad-year-master/public")
base = {"categoryCode": 0, "locationCode": 0, "managementCode": 0, "schoolTypeCode": 0, "yearId": 12, "valueType": 1}
call("enr_states.json", "students-enrollment/public", {**base, "regionCode": "99", "regionType": 10, "dType": 21, "dCode": "99"})
for i in range(1, 39):
    st = f"{i:02d}"
    call(f"enr_dist_{st}.json", "students-enrollment/public", {**base, "regionCode": st, "regionType": 11, "dType": 22, "dCode": st})
for st in ["09", "32"]:
    call(f"sum_dist_{st}.json", "students-summarised-stats/public", {**base, "regionCode": st, "regionType": 11, "dType": 22, "dCode": st})

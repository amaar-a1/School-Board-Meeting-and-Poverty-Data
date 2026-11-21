# Round 5: Israel population by locality and age, census 2022, locality list, National Insurance benefits by locality.
import os, urllib.request, urllib.parse, json, time
OUT = "fetch/out/il5"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush(); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
DS = "https://data.gov.il/api/3/action/datastore_search?limit=32000&resource_id="
for name, rid in [("il_residents_age_current", "64edd0ee-3d5d-43ce-8562-c336c24dbc1f"), ("il_residents_age_a5e7", "a5e7080d-3c37-49c2-8cd0-cb2724809216"),
                  ("il_residents_age_578c", "578c8312-0a87-4eba-a5d0-be8734e9d72f"), ("il_residents_age_16f0", "16f0eeb0-31a0-4edb-bc9d-c9477133c740"),
                  ("il_young_residents", "b8112650-a2f8-41f2-9c05-a9b9483fb4c0"), ("il_localities", "5c78e9fa-c2e2-4771-93ff-7f400a12f7ba"),
                  ("il_localities_en", "8f714b6f-c35c-4b40-a0e7-547b675eee0e"), ("il_census22_pop_households", "38207cf8-afe2-48ed-a3b0-c8f70c796015"),
                  ("il_census22_age", "5474c592-3faa-4298-8783-a8da9acc040f")]:
    get(name + ".json", DS + rid)
get("il_census22_selected.json", DS + "9a9e085f-3bc8-41df-b15f-be0daaf99e30")
for q in ["מקבלי גמלאות לפי יישוב", "הבטחת הכנסה", "ביטוח לאומי יישוב", "רשויות מקומיות", "תלמידים לפי רשות"]:
    get("il_ckan_" + str(abs(hash(q)) % 10**6) + ".json", "https://data.gov.il/api/3/action/package_search?rows=100&q=" + urllib.parse.quote(q))
get("il_org_edu_full.json", "https://data.gov.il/api/3/action/package_search?rows=100&fq=organization:ministry_of_education")
get("il_org_nii.json", "https://data.gov.il/api/3/action/package_search?rows=200&fq=organization:social_security")
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: log.write(f"== dropped {fn}\n"); os.remove(f"{OUT}/{fn}")

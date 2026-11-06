# Temporary: find the exact files and API fields for the next data gaps (US meeting dates, enrollment for
# Germany/Iceland/Ireland, Mexico, Brazil). Writes short reports to fetch/out/disc/.
import json, os, re, urllib.request, urllib.parse, time, traceback
OUT = "fetch/out/disc"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")


def get(url, n=3_000_000, data=None, hdr=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(hdr or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.headers.get("Content-Type", ""), r.headers.get("Content-Length", ""), r.read(n)


def head(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            return f"{r.status} {r.headers.get('Content-Type','')} {r.headers.get('Content-Length','')}"
    except Exception as e:
        return f"ERR {e}"


def step(name, f):
    try:
        res = f()
        log.write(f"== {name}\n{res}\n\n")
    except Exception:
        log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush(); time.sleep(2)


def links(url, pat):
    s, ct, cl, b = get(url)
    t = b.decode("utf-8", "replace")
    hrefs = sorted(set(re.findall(r'(?:href|src)=["\']([^"\']+)["\']', t)))
    return f"{s} {ct} {len(b)}\n" + "\n".join(urllib.parse.urljoin(url, h) for h in hrefs if re.search(pat, h, re.I))[:12000]


# --- CivicSearch: find the API the site uses for a place's meetings
def civic():
    out = []
    s, ct, cl, b = get("https://schools.civicsearch.org/")
    t = b.decode("utf-8", "replace"); open(f"{OUT}/civic_home.html", "w").write(t)
    js = sorted(set(re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', t)))
    out.append("home %s %d; scripts %s" % (s, len(b), js))
    for j in js[:12]:
        u = urllib.parse.urljoin("https://schools.civicsearch.org/", j)
        try:
            _, _, _, jb = get(u, 20_000_000); jt = jb.decode("utf-8", "replace")
            apis = sorted(set(re.findall(r'["\'`](/?api/[A-Za-z0-9_/\-]+)', jt)))
            out.append(f"{u} {len(jb)} apis: {apis}")
            for m in re.finditer(r'api/get_[a-z_]+', jt):
                out.append("  ctx: " + jt[max(0, m.start() - 200): m.end() + 200].replace("\n", " "))
                if len(out) > 80: break
        except Exception as e:
            out.append(f"{u} ERR {e}")
    _, _, _, pb = get("https://schools.civicsearch.org/api/get_place_list", 50_000_000)
    pl = json.loads(pb); open(f"{OUT}/civic_places.json", "wb").write(pb)
    first = pl[0] if isinstance(pl, list) else pl
    out.append("place list type %s len %d first %s" % (type(pl).__name__, len(pl), json.dumps(first)[:800]))
    return "\n".join(out)
step("civicsearch", civic)


def civic_try():
    pl = json.load(open(f"{OUT}/civic_places.json"))
    p = pl[0] if isinstance(pl, list) else None
    out = []
    keys = list(p.keys()) if isinstance(p, dict) else []
    pid = p.get("id") or p.get("place_id") or p.get("slug") or p.get("name") if isinstance(p, dict) else ""
    for path in ["api/get_place?place=%s", "api/get_meetings?place=%s", "api/get_meeting_list?place=%s", "api/get_place_meetings?place=%s",
                 "api/get_place_info?place=%s", "api/place/%s", "api/get_videos?place=%s"]:
        u = "https://schools.civicsearch.org/" + path % urllib.parse.quote(str(pid))
        try:
            s, ct, cl, b = get(u, 200_000); out.append(f"{u} {s} {ct} {b[:600]!r}")
        except Exception as e:
            out.append(f"{u} ERR {e}")
    return f"keys {keys}\n" + "\n".join(out)
step("civicsearch try", civic_try)


# --- Germany: Regionalstatistik GENESIS REST, pupils by Kreis (21111) and population by age (12411)
def genesis():
    out = []
    for base in ["https://www.regionalstatistik.de/genesisws/rest/2020", "https://www-genesis.destatis.de/genesisWS/rest/2020"]:
        for user, pw in (("GAST", "GAST"),):
            u = f"{base}/helloworld/logincheck?username={user}&password={pw}&language=de"
            try:
                s, ct, cl, b = get(u, 5000); out.append(f"{u} {s} {b[:300]!r}")
            except Exception as e:
                out.append(f"{u} ERR {e}")
            for q in ["find/find?term=21111&category=tables&pagelength=50", "catalogue/tables?selection=21111*&pagelength=50"]:
                u = f"{base}/{q}&username={user}&password={pw}&language=de"
                try:
                    s, ct, cl, b = get(u, 60000); out.append(f"{u} {s} {b[:6000]!r}")
                except Exception as e:
                    out.append(f"{u} ERR {e}")
    return "\n".join(out)
step("genesis", genesis)


# --- Iceland: PX-Web tables under education
def hagstofa():
    out = []
    def walk(path, depth):
        u = "https://px.hagstofa.is/pxis/api/v1/is/" + path
        s, ct, cl, b = get(u, 500_000); items = json.loads(b)
        for it in items:
            out.append("  " * depth + f"{path}/{it.get('id')} [{it.get('type')}] {it.get('text')}")
            if it.get("type") == "l" and depth < 2:
                walk(f"{path}/{it['id']}".strip("/"), depth + 1); time.sleep(0.5)
    walk("Samfelag/skolamal", 0)
    return "\n".join(out)
step("hagstofa", hagstofa)


# --- Ireland: Department of Education school-level enrolment files
step("ireland primary", lambda: links("https://www.gov.ie/en/department-of-education/collections/primary-schools-enrolment-figures/", r"\.(xlsx?|csv|ods)|/publications?/|/collections?/"))
step("ireland data on individual schools", lambda: links("https://www.gov.ie/en/collection/63363b-data-on-individual-schools", r"\.(xlsx?|csv|ods)|/publications?/|/collections?/"))
step("ireland cso enrol", lambda: get("https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/EDA42/JSON-stat/2.0/en", 3000)[3][:3000])

# --- Mexico
step("coneval page", lambda: links("https://www.coneval.org.mx/Medicion/Paginas/Pobreza-municipio-2010-2020.aspx", r"\.(zip|xlsx?|csv)"))
step("coneval groups page", lambda: links("https://www.coneval.org.mx/Medicion/Paginas/Pobreza-municipal-por-grupos-de-poblacion-2020.aspx", r"\.(zip|xlsx?|csv)"))
step("coneval zip head", lambda: head("https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip"))
step("inegi iter head", lambda: head("https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip"))
step("datos.gob.mx matricula", lambda: get("https://www.datos.gob.mx/busca/api/3/action/package_search?q=matricula%20municipio&rows=20", 400_000)[3][:8000])
step("sep planeacion", lambda: links("https://www.planeacion.sep.gob.mx/estadisticaeindicadores.aspx", r"\.(zip|xlsx?|csv)|estad"))
step("geoboundaries MEX", lambda: get("https://www.geoboundaries.org/api/current/gbOpen/MEX/ADM2/", 5000)[3][:3000])

# --- Brazil
def misocial():
    u = ("https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=tipo_s:mes_mu&fq=anomes_s:202412*&rows=2&wt=json")
    s, ct, cl, b = get(u, 300_000)
    return b[:6000]
step("mds misocial", misocial)
step("mds vis data", lambda: links("https://aplicacoes.cidadania.gov.br/vis/data3/data-explorer.php", r"\.(csv|json|php)"))
step("ibge sidra census 2022 income table search", lambda: get("https://servicodados.ibge.gov.br/api/v3/agregados?pesquisa=CD", 2_000_000)[3][:12000])
step("inep sinopse", lambda: links("https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica", r"\.(zip|xlsx?)"))
step("geoboundaries BRA", lambda: get("https://www.geoboundaries.org/api/current/gbOpen/BRA/ADM2/", 5000)[3][:3000])
log.close()

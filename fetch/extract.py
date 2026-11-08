# Temporary: Svalbard labour and income pages (Statistics Norway) and the Pitcairn Islands economic review (2023).
import os, urllib.request
OUT = "fetch/out/isl6"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for name, u in {"ssb_arbeid_en.html": "https://www.ssb.no/en/svalbard/arbeid-lonn-og-utdanning",
                "ssb_arbeid_no.html": "https://www.ssb.no/svalbard/arbeid-lonn-og-utdanning",
                "ssb_okonomi_en.html": "https://www.ssb.no/en/svalbard/okonomi",
                "ssb_inntekt_no.html": "https://www.ssb.no/svalbard/inntekt-og-forbruk",
                "ssb_levekar_no.html": "https://www.ssb.no/svalbard/sosiale-forhold-og-kriminalitet",
                "ssb_rapp2023_36.pdf": "https://www.ssb.no/virksomheter-foretak-og-regnskap/virksomheter-og-foretak/artikler/samfunnsforhold-pa-svalbard/_/attachment/inline/234f5e8c-6116-41ab-98b6-2f8a239a11d8:c879531c5dc8a73b44a5e21998882a56fc23db05/RAPP2023-36.pdf",
                "pcn_econ.pdf": "https://static1.squarespace.com/static/6526ff6fef608a3828c13d05/t/65600116a332be611d46c884/1700790554810/Pitcairn+Islands+Economic+Report+-+Final+Report.pdf"}.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180) as r: b = r.read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()

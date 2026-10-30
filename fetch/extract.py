# Temporary: download each territory's 2020 DHC zip and save a small peek at its contents.
import io, os, urllib.request, zipfile
B = "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas"
T = {"gu": "guam", "mp": "commonwealth-of-the-northern-mariana-islands", "vi": "us-virgin-islands", "as": "american-samoa"}
os.makedirs("fetch/out/peek", exist_ok=True)
for ab, name in T.items():
    path = f"/tmp/{ab}.zip"
    if not os.path.exists(path):
        urllib.request.urlretrieve(f"{B}/{name}/demographic-and-housing-characteristics-file/{ab}2020.dhc.zip", path)
    z = zipfile.ZipFile(path)
    with open(f"fetch/out/peek/{ab}_list.txt", "w") as out:
        for i in z.infolist():
            out.write(f"{i.filename}\t{i.file_size}\n")
    if ab == "gu":
        for i in z.infolist():
            with z.open(i) as f:
                head = f.read(3000).decode("latin-1")
            open(f"fetch/out/peek/{ab}_{os.path.basename(i.filename)}.head.txt", "w").write(head)

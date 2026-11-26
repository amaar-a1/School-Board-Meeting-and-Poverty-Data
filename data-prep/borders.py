"""Border changes in the series over time: municipalities split up or merged.

- A split (a new place made out of one or more others): every place keeps its own figures, each year on that year's
  borders, so a parent drops in the year it lost part of its land. The family (parents and new places) is also added
  up as one place on the borders before the split, for the "... by year (earlier borders)" columns, drawn as a dotted
  line beside the place's own.
- A merger (former places joined into one): the merged place's years before the merger are its former places added
  up, so its whole line is on today's borders.
Either way the change goes in the "Border changes" column ("2017: San Miguel was made from Juliaca; 2019: Aa, Bb and
Cc merged into Dd"), which the charts mark with a vertical line.
"""

COL = "Border changes"
# Data files whose builds write border changes themselves (for their own series); population_history.py apply adds
# its own to theirs, and rewrites the column of every other file.
BUILD_WRITES = ("peru", "netherlands")


def skey(t):
    import unicodedata
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()


def both(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def families(edges):
    """edges: (parent, new place, first year). Returns place -> the set of places split from one another."""
    fam = {}
    for p, c, _ in edges:
        u = fam.get(p, {p}) | fam.get(c, {c})
        for m in u: fam[m] = u
    return fam


def family_sum(series, members, first):
    """The members' figures added up each year that all of them have one (a new place counts only from its first
    year: before that it was inside its parents)."""
    ys = sorted(set().union(*(series.get(k, {}).keys() for k in members)))
    out = {}
    for y in ys:
        due = [k for k in members if not (k in first and y < first[k])]
        if due and all(series.get(k, {}).get(y) is not None for k in due):
            out[y] = sum(series[k][y] for k in due)
    return out


def split_texts(edges, members, name):
    made = {}
    for p, c, F in edges:
        if c in members: made.setdefault((F, name(c)), []).append(name(p))
    return [f"{F}: {c} was made from {both(sorted(ps, key=skey))}" for (F, c), ps in sorted(made.items())]


def earlier_borders(series, edges, name):
    """series: place -> {year: value} (counts). For each place in a split: (the family on its earlier borders, the
    places in it, the border-change texts)."""
    first = {c: F for _, c, F in edges}
    out = {}
    for m, members in families(edges).items():
        out[m] = (family_sum(series, members, first), both(sorted((name(k) for k in members), key=skey)), split_texts(edges, members, name))
    return out


def merge_back(series, mergers):
    """mergers: [{"year": "2019", "into": code, "from": [former codes], "names": [former names], "name": new name,
    "rename": a code change only, "part": took in only part of a divided place}] (a merged place that kept one of the former codes lists it in "from" too). Each
    year that still lists the former places (before the merger, or in a source a year behind) becomes them added up,
    where all of them have a figure; a year with only the merged place's own code is on the new borders already.
    Returns place -> its border-change texts."""
    texts = {}
    for m in sorted(mergers, key=lambda m: m["year"]):
        parts, F, new = m["from"], str(m["year"]), m["into"]
        if m.get("part"):   # took in part of a municipality divided among several: marked only
            if new in series: texts.setdefault(new, []).append(f"{F}: part of {both(m.get('names') or parts)} joined {m.get('name') or new}")
            continue
        own = series.get(new, {})
        out, have_at = {}, {}
        others = [k for k in parts if k != new]
        for y in sorted(set().union(own.keys(), *(series.get(k, {}).keys() for k in parts))):
            have = [k for k in parts if series.get(k, {}).get(y) is not None]
            # a year that still lists the former places (before the merger, or a source a year behind) adds them up
            if any(k in have for k in others) or (not others and y < F):
                if len(have) == len(parts): out[y] = sum(series[k][y] for k in parts); have_at[y] = True
            elif y in own: out[y] = own[y]
        # A check on the list: the former places added up should come close to the merged place's first figure. If
        # they don't (a place divided among several, listed under one), the years before aren't added up.
        pre = [y for y in out if have_at.get(y)]
        post = [y for y in out if not have_at.get(y) and y > (pre[-1] if pre else "")]
        if pre and post and int(post[0]) - int(pre[-1]) <= 2 and abs(out[post[0]] / out[pre[-1]] - 1) > 0.15:
            out = {y: v for y, v in out.items() if not have_at.get(y)}
        if out:
            series[new] = out
            if m.get("rename") and parts[0] in texts:   # the same place under a new code keeps its earlier changes
                texts[new] = texts.pop(parts[0]) + texts.get(new, [])
            if not m.get("rename") and any(have_at.get(y) for y in out):   # only where the former places were added up
                texts.setdefault(new, []).append(f"{F}: {both(sorted(m.get('names') or parts, key=skey))} merged into {m.get('name') or new}")
    return texts


def add_texts(old, new):
    """Joins border-change texts, once each, by year."""
    seen = [t.strip() for t in str(old or "").split(";") if t.strip()]
    for t in new:
        if t not in seen: seen.append(t)
    return "; ".join(sorted(seen))

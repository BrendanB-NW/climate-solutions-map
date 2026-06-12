#!/usr/bin/env python3
"""Render The Climate Solutions Map from extracted census JSON. Deterministic — no LLM calls."""
import json, os, re, glob, html

BASE = os.environ.get("CSM_BASE", "/Users/brendanboyd/climate-research")
DATA = os.path.join(BASE, "data")
OUT = os.environ.get("CSM_OUT", os.path.join(BASE, "report"))
RUN2_OUTPUT = "/private/tmp/claude-501/-Users-brendanboyd/577c0838-8a53-4727-91f9-8a0fc2ea094a/tasks/wz2w1qttb.output"
_meta = os.path.join(DATA, "meta.json")
ASOF = json.load(open(_meta))["as_of"] if os.path.exists(_meta) else "June 11, 2026"

SECTORS = [
    ("energy", "Clean Energy Supply", "02-clean-energy.md",
     "How we make and move zero-carbon electricity: every generation source, every storage chemistry and form factor, and the grid hardware that connects them. Solar, wind, and lithium batteries are the mature deployment engine of the whole transition; advanced nuclear, fusion, next-gen geothermal, and long-duration storage are the frontier."),
    ("transport", "Transport", "03-transport.md",
     "Moving people and freight without oil. Light-duty EVs and their battery supply chain are commercially won and scaling; the open battles are heavy trucking, charging at scale, and the hard physics of aviation and shipping fuels."),
    ("buildings", "Buildings", "04-buildings.md",
     "Heating, cooling, and constructing buildings without fossil fuels: heat pumps in every form factor, envelope and windows, smart controls, low-carbon materials, and the refrigerant transition. Most of this technology is mature — the constraint is delivery, financing, and demand, which is exactly where the newest companies cluster."),
    ("industry", "Industry & Manufacturing", "05-industry.md",
     "The hardest-to-abate sector: steel, cement, chemicals, hydrogen, ammonia, process heat, and the minerals supply chain that everything else depends on. This is where the innovation gap is widest and where first-of-a-kind plant financing decides who survives."),
    ("food", "Food, Agriculture & Land Use", "06-food-ag-land.md",
     "Roughly a third of global emissions once land use is counted: alternative proteins, livestock and rice methane, fertilizer, precision and regenerative agriculture, food waste, forests, and blue carbon. Solutions here are unusually behavior- and policy-dependent, and the alt-protein shakeout of 2023–2025 is a live case study in hype-cycle risk."),
    ("cdr", "Carbon Removal & Capture", "07-carbon-removal.md",
     "Pulling CO2 back out of the air and smokestacks and locking it away — or turning it into products. The clearest innovation gap in climate: the IEA pathway needs ~1,000 Mt/yr of removal by 2050 and today's installed base captures a rounding error of that, at $100–1,000/tonne. Almost the entire sector currently lives off voluntary buyers and tax credits."),
    ("enabling", "Enabling Layers", "08-enabling-layers.md",
     "The software, data, markets, and money that make physical decarbonization deployable: carbon accounting and measured emissions, carbon market infrastructure, grid software and VPPs, energy market tooling, climate fintech, and supply-chain decarbonization. Low capex, fast iteration — and directly aimed at the deployment bottlenecks (interconnection, finance, MRV trust) that throttle everything else."),
]

MATURITY_ORDER = ["mature", "scaling", "demonstration", "pilot", "lab"]
M_BADGE = {"mature": "🟢 mature", "scaling": "🟡 scaling", "demonstration": "🟠 demonstration", "pilot": "🔵 pilot", "lab": "⚪ lab"}


def clean_cell(s):
    if not s:
        return "—"
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s.replace("|", "\\|")


def maybe_unescape(s):
    if s and ("&gt;" in s or "&amp;" in s or "&lt;" in s):
        return html.unescape(s)
    return s


def gh_anchor(s):
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())


def load_all():
    censuses = {}
    for path in glob.glob(os.path.join(DATA, "census", "*.json")):
        with open(path) as f:
            rec = json.load(f)
        censuses[(rec["sector"], rec["bucket"])] = rec["census"]
    taxonomies = {}
    for path in glob.glob(os.path.join(DATA, "taxonomy", "*.json")):
        with open(path) as f:
            taxonomies[os.path.basename(path)[:-5]] = json.load(f)
    audits = {}
    for path in glob.glob(os.path.join(DATA, "audit", "*.json")):
        with open(path) as f:
            audits[os.path.basename(path)[:-5]] = json.load(f)
    return censuses, taxonomies, audits


def load_crosscutting():
    """claim + graveyard markdown: prefer saved copies, else pull from run-2 task output."""
    claim_p, grave_p = os.path.join(DATA, "claim.md"), os.path.join(DATA, "graveyard.md")
    claim = grave = None
    if os.path.exists(claim_p):
        claim = open(claim_p).read()
    if os.path.exists(grave_p):
        grave = open(grave_p).read()
    if claim is None or grave is None:
        with open(RUN2_OUTPUT) as f:
            result = json.load(f)["result"]
        claim = claim or maybe_unescape(result.get("claimAssessment") or "")
        grave = grave or maybe_unescape(result.get("graveyard") or "")
        open(claim_p, "w").write(claim)
        open(grave_p, "w").write(grave)
    return claim, grave


def company_row(c):
    name = clean_cell(c.get("name"))
    src = (c.get("source") or "").strip()
    status = c.get("status", "operating")
    if status == "bankrupt-shutdown":
        name = "⚠️ " + name
    if src.startswith("http"):
        name = f"[{name}]({src})"
    sig = clean_cell(c.get("signal"))
    suffix = {"acquired": " · **acquired**", "bankrupt-shutdown": " · **☠ shut down**", "uncertain": " · *status unverified*"}.get(status, "")
    sig = (sig if sig != "—" else "") + suffix
    return f"| {name} | {c.get('role', '—')} | {clean_cell(c.get('what'))} | {sig or '—'} |"


def render_variation(v):
    lines = [f"**{v.get('name', 'Unnamed variation')}** · `{M_BADGE.get(v.get('maturity'), v.get('maturity', '?'))}`",
             "", clean_cell(v.get("description")).replace("\\|", "|"), ""]
    comps = v.get("companies", [])
    if comps:
        lines += ["| Company | Type | What they do | Signal / status |", "|---|---|---|---|"]
        lines += [company_row(c) for c in comps]
    else:
        lines.append("*No companies identified.*")
    ws = v.get("white_space")
    if ws:
        lines += ["", f"> **White space:** {clean_cell(ws).replace(chr(92) + '|', '|')}"]
    lines.append("")
    return "\n".join(lines)


def render_bucket(census):
    name = census.get("bucket", "Unnamed bucket")
    lines = [f"### {name}", ""]
    for v in census.get("variations", []):
        lines.append(render_variation(v))
    srcs = sorted({s.strip() for s in census.get("sources", []) if s and s.strip().startswith("http")})
    if srcs:
        lines += ["<details><summary>Key sources — " + name + "</summary>", ""]
        lines += [f"- {s}" for s in srcs]
        lines += ["", "</details>", ""]
    return "\n".join(lines)


def sector_stats(buckets):
    n_var = sum(len(c.get("variations", [])) for c in buckets)
    comps = [c2 for c in buckets for v in c.get("variations", []) for c2 in v.get("companies", [])]
    dead = sum(c.get("status") == "bankrupt-shutdown" for c in comps)
    acq = sum(c.get("status") == "acquired" for c in comps)
    unc = sum(c.get("status") == "uncertain" for c in comps)
    mat = {}
    for c in buckets:
        for v in c.get("variations", []):
            mat[v.get("maturity")] = mat.get(v.get("maturity"), 0) + 1
    return {"buckets": len(buckets), "variations": n_var, "entries": len(comps),
            "unique": len({c.get("name", "").strip().lower() for c in comps}),
            "dead": dead, "acquired": acq, "uncertain": unc, "maturity": mat}


def glance_line(buckets):
    parts = []
    for c in buckets:
        counts = {}
        for v in c.get("variations", []):
            counts[v.get("maturity")] = counts.get(v.get("maturity"), 0) + 1
        seg = ", ".join(f"{counts[m]} {m}" for m in MATURITY_ORDER if m in counts)
        nm = c.get("bucket", "?")
        nm = nm if len(nm) <= 48 else nm[:45] + "..."
        parts.append(f"{nm} ({seg})")
    return " · ".join(parts)


def render_audit(audit):
    lines = ["#### Verification audit notes", ""]
    flags = audit.get("status_flags", [])
    if flags:
        lines.append("Status corrections/nuances found by the audit pass:")
        for fl in flags:
            ev = fl.get("evidence", "")
            ev_md = f" ([evidence]({ev}))" if str(ev).startswith("http") else (f" — {ev}" if ev else "")
            lines.append(f"- **{fl.get('company')}** — {fl.get('finding')}{ev_md}")
        lines.append("")
    missing = audit.get("missing", [])
    if missing:
        lines.append("Notable omissions the audit flagged (not yet incorporated into tables):")
        lines += [f"- *{m.get('where')}*: {m.get('what')}" for m in missing]
        lines.append("")
    failures = audit.get("notable_failures", [])
    if failures:
        lines.append("<details><summary>Sector failures noted by audit</summary>")
        lines.append("")
        lines += [f"- {x}" for x in failures]
        lines += ["", "</details>", ""]
    return "\n".join(lines) if (flags or missing or failures) else ""


def render_sector(key, title, intro, censuses, taxonomies, audits):
    tax = taxonomies.get(key, {}).get("buckets", [])
    order = [b["name"] for b in tax]
    have = {b: c for (k, b), c in censuses.items() if k == key}
    ordered = [have[n] for n in order if n in have] + [c for n, c in sorted(have.items()) if n not in order]
    st = sector_stats(ordered)
    lines = [f"## {title}", "", intro, "",
             f"*{st['buckets']} solution areas · {st['variations']} variations · {st['entries']} company entries"
             f" ({st['unique']} unique companies; {st['dead']} marked dead, {st['acquired']} acquired, {st['uncertain']} unverified)*", "",
             f"**Maturity at a glance (variations per stage):** {glance_line(ordered)}", ""]
    missing_buckets = [n for n in order if n not in have]
    if missing_buckets:
        lines += ["> ⚠️ *Census incomplete for: " + "; ".join(missing_buckets) + "*", ""]
    if key in audits:
        a = render_audit(audits[key])
        if a:
            lines += [a]
    lines += ["**Solution areas:** " + " · ".join(f"[{c.get('bucket')}](#{gh_anchor(c.get('bucket', ''))})" for c in ordered), ""]
    for c in ordered:
        lines.append(render_bucket(c))
    return "\n".join(lines), st


def collect_white_space(censuses):
    rows = []
    titles = {k: t for k, t, _, _ in SECTORS}
    for (k, b), c in sorted(censuses.items()):
        for v in c.get("variations", []):
            ws = v.get("white_space")
            if ws:
                rows.append((titles.get(k, k), b, v.get("name", "?"), ws))
    return rows


def nav_line(idx, chapters):
    parts = []
    if idx > 0:
        pf, pt = chapters[idx - 1][0], chapters[idx - 1][1]
        parts.append(f"[← {pt}]({pf})")
    parts.append("[🏠 Start here](README.md)")
    if idx < len(chapters) - 1:
        nf, nt = chapters[idx + 1][0], chapters[idx + 1][1]
        parts.append(f"[{nt} →]({nf})")
    return " · ".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    censuses, taxonomies, audits = load_all()
    claim, grave = load_crosscutting()

    sector_files, totals = [], {"buckets": 0, "variations": 0, "entries": 0, "dead": 0, "acquired": 0, "uncertain": 0}
    all_names = set()
    sector_bodies = []

    for key, title, fname, intro in SECTORS:
        body, st = render_sector(key, title, intro, censuses, taxonomies, audits)
        sector_files.append((key, title, fname, st))
        sector_bodies.append((fname, title, body))
        for k2 in ("buckets", "variations", "entries", "dead", "acquired", "uncertain"):
            totals[k2] += st[k2]
        for (k, b), c in censuses.items():
            if k == key:
                for v in c.get("variations", []):
                    for comp in v.get("companies", []):
                        all_names.add(comp.get("name", "").strip().lower())

    ws_rows = collect_white_space(censuses)
    ws_lines = ["## White-space index", "",
                "Every variation the census flagged as having few credible players, with the researcher's note on why — physics, economics, or incumbency. Raw founder/investor prospecting data; judge each entry critically.", "",
                "| Sector | Solution area | Variation | Why it's open |", "|---|---|---|---|"]
    ws_lines += [f"| {clean_cell(a)} | {clean_cell(b)} | {clean_cell(c)} | {clean_cell(d)} |" for a, b, c, d in ws_rows]
    ws_doc = "\n".join(ws_lines) + "\n"

    # Reading-order chapter list: (filename, short title, body)
    chapters = [("01-does-the-claim-hold.md", "Does the claim hold?", claim)]
    chapters += sector_bodies
    chapters += [("09-white-space-index.md", "White-space index", ws_doc),
                 ("10-graveyard.md", "The graveyard", grave)]

    for i, (fname, title, body) in enumerate(chapters):
        nav = nav_line(i, chapters)
        page = f"{nav}\n\n*Part of **The Climate Solutions Map** · data as of {ASOF}*\n\n---\n\n{body}\n\n---\n\n{nav}\n"
        open(os.path.join(OUT, fname), "w").write(page)

    methodology = f"""## Methodology & caveats

- Compiled {ASOF} by ~130 parallel AI research agents (Anthropic's Claude, with live web search; 2024–2026 sources preferred), orchestrated and reviewed by a human. Company entries carry a source link on the company name.
- **Maturity** is rated per variation: mature (widely deployed, cost-competitive) → scaling → demonstration → pilot → lab.
- **Coverage is "notable players," not a registry.** 3–10 companies per variation was the target; absence from this map is not evidence a company doesn't exist or matter.
- Failed companies (⚠️ / ☠) are kept deliberately — they are white-space evidence, not noise. See [the graveyard](10-graveyard.md).
- Only Clean Energy received a dedicated second-pass verification audit; other sectors rely on each researcher's own status checks. Treat any single company fact as unverified until you check the linked source — this is AI-compiled research, not investment advice.
- A company may legitimately appear under several variations (e.g., diversified incumbents). "Company entries" counts rows; "unique companies" deduplicates by name.
- Text and data are licensed [CC BY 4.0](LICENSE) — share and adapt freely with attribution. Not investment advice.
"""

    legend = "**Legend:** 🟢 mature · 🟡 scaling · 🟠 demonstration · 🔵 pilot · ⚪ lab — rated per variation. ⚠️/☠ = shut down or bankrupt (kept as data). *(audit add)* = added by verification pass."

    preface = f"""## Why this map exists

You may have heard some version of this claim:

> *"All of the climate solutions we need already exist — we just need to start implementing them WAY faster."*

This project began as a simple question about that claim: **okay — what are all of these solutions, and who is actually building them?**

This map is the answer. It is a census of every climate solution we could find, every distinct technical variation of each one, and the companies implementing them — with a verdict on the claim itself in [chapter 1](01-does-the-claim-hold.md). It was compiled on {ASOF} by a fleet of ~130 AI research agents (Anthropic's Claude) using live web search, orchestrated and reviewed by a human. Every company entry links to a source you can check yourself.

**New to GitHub?** You don't need an account — this is just a collection of linked pages. Click any blue link to open a chapter, and use the `← / 🏠 / →` links at the top of every page (or your browser's Back button) to get around. Suggested path: chapter 1 for the verdict, then whichever sector you're curious about, then the white-space index if you want to know what *isn't* being built yet.
"""

    readme = [f"# The Climate Solutions Map", "",
              f"*A census of climate solutions, their technical variations, and the companies implementing them. Data as of {ASOF}.*", "",
              preface,
              f"**{totals['entries']} company entries** ({len(all_names)} unique companies) across **{totals['buckets']} solution areas** and **{totals['variations']} distinct technical variations** in 7 sectors — including {totals['dead']} documented failures and {totals['acquired']} acquisitions kept as market evidence.", "",
              legend, "", "## Contents", "",
              "1. [Does the claim hold? — \"the solutions already exist\"](01-does-the-claim-hold.md) — the verdict on the slogan that motivated this research"]
    for i, (key, title, fname, st) in enumerate(sector_files, start=2):
        readme.append(f"{i}. [{title}]({fname}) — {st['buckets']} areas · {st['variations']} variations · {st['entries']} companies")
    readme += [f"9. [White-space index](09-white-space-index.md) — {len(ws_rows)} under-populated variations and why",
               f"10. [The graveyard](10-graveyard.md) — 31 documented failures and the patterns behind them", "",
               "*(There is also a [single-file version](climate-solutions-map-FULL.md) of the whole map — note GitHub won't preview a file that large in the browser, so it's best downloaded for offline search. The chapters above are the easy way to read.)*", "",
               "## Sector overview", "",
               "| Sector | Solution areas | Variations | Company entries | Dead | Acquired |", "|---|---|---|---|---|---|"]
    for key, title, fname, st in sector_files:
        readme.append(f"| [{title}]({fname}) | {st['buckets']} | {st['variations']} | {st['entries']} | {st['dead']} | {st['acquired']} |")
    fresh = """## Keeping it fresh

Company statuses drift fast — the graveyard chapter is proof. This repo ships its raw data (`data/`) and its renderer (`tools/render_report.py`), and a GitHub Action (`.github/workflows/refresh-data.yml`) can re-verify company statuses against recent news monthly and open a pull request with updates (requires the repo owner to configure an `ANTHROPIC_API_KEY` secret). Rendering is deterministic: `CSM_BASE=. CSM_OUT=. python3 tools/render_report.py`.
"""
    readme += ["", fresh, methodology]
    open(os.path.join(OUT, "README.md"), "w").write("\n".join(readme) + "\n")

    full = ["# The Climate Solutions Map", "",
            f"*A census of climate solutions, their technical variations, and the companies implementing them. Data as of {ASOF}.*", "",
            f"**{totals['entries']} company entries** ({len(all_names)} unique) · **{totals['buckets']} solution areas** · **{totals['variations']} variations** · 7 sectors.", "",
            legend, "", "---", "", claim, "", "---", ""]
    full += [body + "\n\n---\n" for _, _, body in sector_bodies]
    full += ["", ws_doc, "", "---", "", grave, "", "---", "", methodology]
    open(os.path.join(OUT, "climate-solutions-map-FULL.md"), "w").write("\n".join(full) + "\n")

    print(f"rendered {len(sector_files)} sectors -> {OUT}")
    print(f"totals: {totals} | unique companies: {len(all_names)} | white-space rows: {len(ws_rows)}")
    for key, title, fname, st in sector_files:
        print(f"  {fname:28s} {st['buckets']:2d} buckets {st['variations']:3d} variations {st['entries']:4d} entries")


if __name__ == "__main__":
    main()

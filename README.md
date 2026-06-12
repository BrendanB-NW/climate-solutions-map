# The Climate Solutions Map

*A census of climate solutions, their technical variations, and the companies implementing them. Data as of June 11, 2026.*

## Why this map exists

You may have heard some version of this claim:

> *"All of the climate solutions we need already exist — we just need to start implementing them WAY faster."*

This project began as a simple question about that claim: **okay — what are all of these solutions, and who is actually building them?**

This map is the answer. It is a census of every climate solution we could find, every distinct technical variation of each one, and the companies implementing them — with a verdict on the claim itself in [chapter 1](01-does-the-claim-hold.md). It was compiled on June 11, 2026 by a fleet of ~130 AI research agents (Anthropic's Claude) using live web search, orchestrated and reviewed by a human. Every company entry links to a source you can check yourself.

**New to GitHub?** You don't need an account — this is just a collection of linked pages. Click any blue link to open a chapter, and use the `← / 🏠 / →` links at the top of every page (or your browser's Back button) to get around. Suggested path: chapter 1 for the verdict, then whichever sector you're curious about, then the white-space index if you want to know what *isn't* being built yet.

**4069 company entries** (3267 unique companies) across **63 solution areas** and **638 distinct technical variations** in 7 sectors — including 166 documented failures and 153 acquisitions kept as market evidence.

**Legend:** 🟢 mature · 🟡 scaling · 🟠 demonstration · 🔵 pilot · ⚪ lab — rated per variation. ⚠️/☠ = shut down or bankrupt (kept as data). *(audit add)* = added by verification pass.

## Contents

1. [Does the claim hold? — "the solutions already exist"](01-does-the-claim-hold.md) — the verdict on the slogan that motivated this research
2. [Clean Energy Supply](02-clean-energy.md) — 9 areas · 84 variations · 574 companies
3. [Transport](03-transport.md) — 9 areas · 95 variations · 710 companies
4. [Buildings](04-buildings.md) — 9 areas · 96 variations · 613 companies
5. [Industry & Manufacturing](05-industry.md) — 9 areas · 105 variations · 600 companies
6. [Food, Agriculture & Land Use](06-food-ag-land.md) — 9 areas · 71 variations · 445 companies
7. [Carbon Removal & Capture](07-carbon-removal.md) — 9 areas · 90 variations · 437 companies
8. [Enabling Layers](08-enabling-layers.md) — 9 areas · 97 variations · 690 companies
9. [White-space index](09-white-space-index.md) — 371 under-populated variations and why
10. [The graveyard](10-graveyard.md) — 31 documented failures and the patterns behind them

*(There is also a [single-file version](climate-solutions-map-FULL.md) of the whole map — note GitHub won't preview a file that large in the browser, so it's best downloaded for offline search. The chapters above are the easy way to read.)*

## Sector overview

| Sector | Solution areas | Variations | Company entries | Dead | Acquired |
|---|---|---|---|---|---|
| [Clean Energy Supply](02-clean-energy.md) | 9 | 84 | 574 | 28 | 18 |
| [Transport](03-transport.md) | 9 | 95 | 710 | 53 | 31 |
| [Buildings](04-buildings.md) | 9 | 96 | 613 | 14 | 32 |
| [Industry & Manufacturing](05-industry.md) | 9 | 105 | 600 | 16 | 8 |
| [Food, Agriculture & Land Use](06-food-ag-land.md) | 9 | 71 | 445 | 27 | 10 |
| [Carbon Removal & Capture](07-carbon-removal.md) | 9 | 90 | 437 | 10 | 11 |
| [Enabling Layers](08-enabling-layers.md) | 9 | 97 | 690 | 18 | 43 |

## Keeping it fresh

Company statuses drift fast — the graveyard chapter is proof. This repo ships its raw data (`data/`) and its renderer (`tools/render_report.py`), and a GitHub Action (`.github/workflows/refresh-data.yml`) can re-verify company statuses against recent news monthly and open a pull request with updates (requires the repo owner to configure an `ANTHROPIC_API_KEY` secret). Rendering is deterministic: `CSM_BASE=. CSM_OUT=. python3 tools/render_report.py`.

## Methodology & caveats

- Compiled June 11, 2026 by ~130 parallel AI research agents (Anthropic's Claude, with live web search; 2024–2026 sources preferred), orchestrated and reviewed by a human. Company entries carry a source link on the company name.
- **Maturity** is rated per variation: mature (widely deployed, cost-competitive) → scaling → demonstration → pilot → lab.
- **Coverage is "notable players," not a registry.** 3–10 companies per variation was the target; absence from this map is not evidence a company doesn't exist or matter.
- Failed companies (⚠️ / ☠) are kept deliberately — they are white-space evidence, not noise. See [the graveyard](10-graveyard.md).
- Only Clean Energy received a dedicated second-pass verification audit; other sectors rely on each researcher's own status checks. Treat any single company fact as unverified until you check the linked source — this is AI-compiled research, not investment advice.
- A company may legitimately appear under several variations (e.g., diversified incumbents). "Company entries" counts rows; "unique companies" deduplicates by name.
- Text and data are licensed [CC BY 4.0](LICENSE) — share and adapt freely with attribution. Not investment advice.


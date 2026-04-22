# Contributing to UVI

---

## The One Rule That Cannot Break

**All UVI math lives in `uvi_engine.py`. Never put formulas anywhere else.**

If you find yourself writing a calculation in `app.py`, stop and move it to the engine. This keeps scores consistent across every view, every run, and every update.

---

## Repository Structure

```
UVI-Analytics/
├── app.py              — Streamlit interface (display only — no math here)
├── uvi_engine.py       — All UVI calculations (single source of truth)
├── update_data.py      — Daily Statcast pull via pybaseball
├── requirements.txt    — Python dependencies
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .streamlit/
│   └── config.toml     — Dark theme settings
└── assets/
    ├── header.png       — App header banner
    ├── icon.png         — Browser tab icon
    └── stadium_bg.jpg  — Background image
```

**Data files (CSVs) are NOT in the repository.** They live in the GitHub Release
and are downloaded automatically by the app on first load. Do not commit CSVs to
the repo — they are excluded by `.gitignore`.

---

## Adding New Data

To update or add data files:

1. Generate the new CSV using the pipeline scripts
2. Create a new GitHub Release (e.g. `v2.2.0`)
3. Attach the updated CSV files as release assets
4. Update `GITHUB_RELEASE_URL` in `uvi_engine.py` to point to the new release
5. Push the code change and reboot the Streamlit app

---

## Formula Changes

Before changing anything in the UVI formula:

1. Document why the change improves accuracy
2. Run the validation check against known reference players
3. Note that changing `LEAGUE_MEAN` or `MULTIPLIER` re-scales all historical scores
   — this requires a CHANGELOG entry and a version bump

**Known reference players for validation:**

| Player | Role | Expected tier | Notes |
|--------|------|--------------|-------|
| Paul Skenes | Pitcher | Impact Player | Historic 2025 season |
| Garrett Crochet | Pitcher | Impact Player | Cy Young contender |
| Aaron Judge | Hitter | Impact Player | MVP-level |
| Shohei Ohtani | Hitter | Impact Player | Two-way elite |
| Byron Buxton | Hitter | Proven Starter | Speed bonus should be visible |

---

## Daily Update Script

`update_data.py` appends new game records to the master CSVs. Rules:

- Never overwrite — always append
- Always log what was pulled and the row count added
- If a `game_pk` already exists, skip it (deduplication built in)
- If pybaseball errors, log it and exit cleanly — do not corrupt existing data

---

## Tier System

Tiers use baseball-native language. Do not change these without a version bump:

| Score | Tier |
|-------|------|
| 160+  | Impact Player |
| 130–159 | Proven Starter |
| 115–129 | Solid Contributor |
| 90–114 | Roster Average |
| 70–89 | Fringe Roster |
| <70 | DFA Candidate |

---

## Reliability Thresholds

| Role | Threshold | Notes |
|------|-----------|-------|
| Pitchers | 15 pitches | Short outings are genuinely small sample |
| Hitters (full) | 10 pitches | Typical 3–4 PA starter game |
| Hitters (partial) | 6–9 pitches | Shown as dim dot with caution note |
| Hitters (very low) | <6 pitches | Pinch hit / early exit — open grey circle |

---

## Developed by

**Charles "Charlie" Hildbold**
Data Analytics, M.S.
Unified Value Index, 2025

# UVI — Unified Value Index
### Pitch-by-Pitch MLB Performance Analytics · v3.0.0

UVI measures every MLB player on a pitch-by-pitch basis, normalized across all 30 stadiums and positions. Every pitch thrown or seen contributes to a player's score, weighted by two simultaneous leverage factors: count context and win probability impact. The result is a park-neutralized performance score where 100 equals league average and each 50 points represents one standard deviation.

**Live app:** uvi-analytics.streamlit.app
**Methodology:** charleshildbold.com/portfolio
**Built by:** Charles "Charlie" Hildbold — M.S. Data Analytics

---

## What's New in v3.0

- **Player-first architecture** — players who changed teams now appear as a single entry with full cross-team game logs and an `all_teams` column showing every team they played for
- **2025 Postseason data** — separate season toggle for Wild Card, Division Series, Championship Series, and World Series
- **Home landing page** — live snapshot cards showing top hitter, top starting pitcher, and biggest riser; player search; quick top-10 leaderboards
- **Three-way pitcher leaderboard** — Hitter, Starting Pitcher, and All Pitchers with automatic role classification based on average pitches per game
- **Fixed game detail date** — always defaults to the player's most recent game
- **Shift column removed** from game log display

---

## Season Coverage

| Season | Description | Pitches |
|--------|-------------|---------|
| 2025 Regular Season | Full season, all 30 teams | 711,897 |
| 2025 Postseason | Wild Card through World Series | TBD |
| 2026 Current Season | Live, updated daily | Growing |

---

## What's in This Repo

```
app.py                    — Streamlit application (display only)
uvi_engine.py             — Core calculation engine (all math lives here)
update_2026_daily.py      — Daily update script for 2026 live data
pull_2026_components.py   — Sprint speed, OAA, running splits
pull_2025_playoffs.py     — One-time 2025 postseason data pull
daily_update.bat          — Windows batch file for daily updates
pull_playoffs.bat         — Windows batch file for playoff data pull
rebuild_season_totals.py  — Player-id grouping fix (run once)
```

---

## Data Architecture

All CSV data files are hosted on GitHub Releases v3.0.0 and downloaded automatically on first load. The app uses `requests` with redirect following to handle GitHub's S3 asset delivery.

**2025 Regular Season (cached after first download):**
- master_hitter_games_2025.csv
- master_pitcher_games_2025.csv
- hitter_season_2025.csv
- pitcher_season_2025.csv
- hitter_game_stats_2025.csv
- pitcher_game_stats_2025.csv

**2025 Postseason (cached after first download):**
- master_hitter_games_2025_playoffs.csv
- master_pitcher_games_2025_playoffs.csv
- hitter_season_2025_playoffs.csv
- pitcher_season_2025_playoffs.csv

**2026 Live Season (re-downloads every session):**
- master_hitter_games_2026.csv
- master_pitcher_games_2026.csv
- hitter_season_2026.csv
- pitcher_season_2026.csv
- last_updated.txt
- outs_above_average_2026.csv
- running_splits_2026.csv
- sprint_speed_2026.csv

---

## The Formula

```
spp      = Σ(weighted_shift) / Σ(pitch_count)
raw_uvi  = 100 + (spp − LEAGUE_MEAN) × MULTIPLIER
uvi      = raw_uvi ÷ park_factor    [hitters]
uvi      = raw_uvi × park_factor    [pitchers]

count_leverage  = {3-2: 1.6×, 2-2: 1.5×, 1-2: 1.4× ...}
win_prob_lev    = clip(|Δwin_prob| × 10, 0.5, 3.0)
leverage        = count_lev × win_prob_lev
weighted_value  = delta_run_exp × leverage
```

**Complete UVI (hitters):**
```
complete_uvi = batting_uvi
             + speed_bonus      (±10 pts)
             + hustle_bonus     (±8 pts)
             + defense_bonus    (±15 pts)
             + burst_bonus      (±3 pts)
```

---

## Validation

Validated against established Statcast-era metrics on the full 2025 season:

| Metric | r | Sample |
|--------|---|--------|
| Hitter UVI vs wOBA | +0.769 | n=308, 250+ PA |
| SP UVI vs FIP | −0.807 | n=191, 50+ IP |
| SP UVI vs ERA | −0.823 | n=191, 50+ IP |

---

## Score Tiers

| Score | Tier |
|-------|------|
| 160+ | 🔥 Impact Player |
| 130–159 | ⭐ Proven Starter |
| 115–129 | 📈 Solid Contributor |
| 90–114 | ⚾ Roster Average |
| 70–89 | 📉 Fringe Roster |
| <70 | ⚠️ DFA Candidate |

Baseline = 100 · Each 50 points = 1 standard deviation · All scores park-neutralized

---

## Frozen Constants

Derived from the complete 2025 MLB season. Never change between runs.

| Constant | Value |
|----------|-------|
| H_MEAN | 0.01343597 |
| H_MULT | 3921.8597 |
| P_MEAN | −0.01680715 |
| P_MULT | 4723.5424 |
| League Avg Speed | 27.3204 ft/sec |
| League Avg Burst | 2.5785 ft |

---

## Daily Update Workflow

Each morning during the 2026 season:

1. Double-click `daily_update.bat`
2. Upload 5 changed files to GitHub Release v3.0.0:
   - master_hitter_games_2026.csv
   - master_pitcher_games_2026.csv
   - hitter_season_2026.csv
   - pitcher_season_2026.csv
   - last_updated.txt
3. Reboot Streamlit Cloud

---

## Tech Stack

Python · Streamlit · Plotly · Pandas · NumPy · pybaseball · Statcast API · GitHub Releases · Streamlit Cloud

---

## Version History

| Version | Description |
|---------|-------------|
| v1.0.0 | Initial UVI engine and validation |
| v2.0.0 | Streamlit app deployment, full 2025 season |
| v2.1.0 | Component bonuses, leaderboard, simulator |
| v2.2.0 | 2026 live season, daily updates, season toggle |
| v3.0.0 | Player-first architecture, 2025 postseason, home page, pitcher role classification |

# ⚾ Unified Value Index (UVI)
### MLB Performance Audit Engine — 2025

> *Every player. Every pitch. Every park. One number that tells the whole story.*

---

## What is UVI?

The **Unified Value Index** measures every MLB player — pitchers and hitters — on a
pitch-by-pitch basis, normalized across all 30 stadiums and positions.

Unlike ERA, WAR, or OPS, UVI audits the **process** behind each pitch: who performed
when the game was on the line, who hustled harder than their average, and who made
elite defensive plays on difficult chances. The result is a single number updated
after every pitch of every game.

**Baseline = 100 (league average).** Everything above is better, everything below
is worse. A 160 means roughly two standard deviations above the league — that is an
Impact Player.

---

## Score Tiers

| Score | Tier | What it means |
|-------|------|---------------|
| 160+  | 🔥 Impact Player | Historic — 2+ std above average |
| 130–159 | ⭐ Proven Starter | Clear top-of-roster contributor |
| 115–129 | 📈 Solid Contributor | Consistent positive value |
| 90–114 | ⚾ Roster Average | Professional baseline |
| 70–89 | 📉 Fringe Roster | Below replacement threshold |
| <70 | ⚠️ DFA Candidate | Significant negative contribution |

---

## The Three Gears

| Gear | Name | What it measures |
|------|------|-----------------|
| ⚙️ Gear 1 | **Discipline** | Count leverage — 3-2 battles, 0-2 holes, count management |
| ⚙️ Gear 2 | **Impact** | Win Probability weighting — clutch performance vs. liability |
| ⚙️ Gear 3 | **Neutralizer** | Park factors across all 30 stadiums |

---

## The Formula

```
spp      = Σ(weighted_shift) / Σ(pitch_count)
raw_uvi  = 100 + (spp − LEAGUE_MEAN) × MULTIPLIER
uvi      = raw_uvi ÷ park_factor   [hitters]
uvi      = raw_uvi × park_factor   [pitchers]
```

**Leverage weighting:**
```
count_leverage  = {3-2: 1.6×,  2-2: 1.5×,  1-2: 1.4×,  0-0: 1.0×  ...}
win_prob_lev    = clip(|Δwin_probability| × 10,  min=0.5,  max=3.0)
leverage        = count_lev × win_prob_lev
```

A strikeout on 3-2 in a tie game = **~4–5× more** than a first-pitch called strike in a blowout.

**Complete UVI (hitters):**
```
complete_uvi = batting_uvi + speed_bonus + hustle_bonus + defense_bonus + burst_bonus
```

---

## Hustle Is Measured Independently of Talent

```
speed_bonus  = (player_sprint_speed − league_avg_27.32) × 2.0    [±10 pts max]
hustle_bonus = (play_hyper_speed − personal_avg_speed) / std × 5  [±8 pts max]
```

A slow player who runs harder than their own average earns a **positive hustle score**,
independent of their raw speed. A fast player who coasts below their average is penalized
regardless of talent. This is a genuine differentiator — no public metric captures this.

---

## Reliability System

| Pitches | Hitters | Pitchers |
|---------|---------|---------|
| 0–5 | ○ Open grey — pinch hit / early exit | ○ Open grey |
| 6–9 | ◉ Dim grey — partial game | ○ Open grey |
| 10–14 | ● Gold — full starter reliability | ○ Open grey |
| 15+ | ● Gold | ● Gold |

Thresholds are data-derived from the full 2025 season std deviation analysis.

---

## App Features

- **Player Audit** — season UVI, last 7 games, complete UVI breakdown by component,
  rolling trend chart, monthly breakdown, full game log with download
- **Game Detail Panel** — select any game to see the full box score (K, IP, ERA, AVG,
  OPS, exit velocity, xwOBA) alongside the UVI score with a plain-English game note
- **Leaderboard** — full 30-team rankings, filterable by team, role, and minimum games
- **Simulator** — project any player into any stadium with weather, opposition, rest,
  and time-of-day adjustments
- **Methodology** — full formula documentation for analysts and front office staff

---

## Data

| Source | Coverage | Records |
|--------|----------|---------|
| Statcast (raw pitch) | All 30 teams, full 2025 season | 711,897 pitches |
| Sprint Speed | All 30 teams, 617 players | Season averages |
| Outs Above Average | All 30 teams, 518 players | Season totals |
| Running Splits | All 30 teams, 549 players | Burst/first-step |

---

## Repository Structure

```
uvi/
├── app.py                         # Streamlit interface — display only
├── uvi_engine.py                  # All UVI calculations — single source of truth
├── update_data.py                 # Daily auto-update via pybaseball
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Dark theme
├── assets/
│   ├── header.png                 # Brand header
│   ├── icon.png                   # App icon
│   └── stadium_bg.jpg             # Background (optional)
└── data/
    ├── master_hitter_games_2025.csv
    ├── master_pitcher_games_2025.csv
    ├── hitter_season_2025.csv
    ├── pitcher_season_2025.csv
    ├── hitter_game_stats_2025.csv
    └── pitcher_game_stats_2025.csv
```

**Rule:** All math lives in `uvi_engine.py`. `app.py` is display only. Never put
formulas anywhere else.

---

## Setup

```bash
git clone https://github.com/yourusername/uvi-engine.git
cd uvi-engine
pip install -r requirements.txt
streamlit run app.py
```

**Requirements:** Python 3.10+, ~500MB disk for full 2025 data.

---

## Daily Auto-Update (2026 Season)

```bash
python update_data.py              # yesterday's games
python update_data.py --date 2026-04-15
python update_data.py --full-season 2026

# Cron — runs daily at 6 AM (Mac/Linux)
0 6 * * * cd /path/to/uvi && python update_data.py >> logs/update.log 2>&1
```

---

## Constants (frozen — never change between runs)

| Constant | Value | Notes |
|----------|-------|-------|
| P_MEAN | -0.01680715 | League mean weighted shift/pitch (pitchers) |
| P_MULT | 4723.54 | 50 UVI pts per std dev (pitchers) |
| H_MEAN | 0.01343597 | League mean weighted shift/pitch (hitters) |
| H_MULT | 3921.86 | 50 UVI pts per std dev (hitters) |
| League Avg Speed | 27.32 ft/sec | Sprint speed baseline |

---

## Roadmap

### Phase 1 — Current ✅
- Full 2025 season, all 30 teams
- Six-component Complete UVI
- Game detail panel with traditional stats
- Daily auto-update

### Phase 2 — Near Term
- Live in-game pitch-by-pitch tracking
- 2024 historical comparison
- Multi-year trend views

### Phase 3 — Commercial
- Pre-game situational intelligence (weather + matchup modeling)
- Sportsbook odds comparison overlay
- Team dashboard licensing
- API access

---

## Terminology

| Term | Definition |
|------|-----------|
| **Impact Player** | 160+ UVI — historic value, 2+ std above league |
| **Proven Starter** | 130–159 — clear top-of-roster contributor |
| **Solid Contributor** | 115–129 — consistent positive value |
| **Roster Average** | 90–114 — professional baseline |
| **Fringe Roster** | 70–89 — below replacement threshold |
| **DFA Candidate** | <70 — significant negative contribution |
| **Stadium Effect** | UVI adjustment for moving between parks |
| **Hustle Bonus** | Effort relative to personal average — rewards hard running |
| **Complete UVI** | Batting + speed + hustle + defense + burst |

---

## About

Developed by **Charles "Charlie" Hildbold**
Data Analytics, M.S.

*UVI is an independent research project. All data sourced from MLB Statcast via
Baseball Savant. Not affiliated with or endorsed by Major League Baseball.*

---

## License

© 2025 Charles Hildbold. All rights reserved.
The UVI formula, methodology, and scoring system are proprietary.
Code provided for demonstration purposes. Contact for licensing.

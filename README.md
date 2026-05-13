# UVI — Unified Value Index
### Pitch-by-Pitch MLB Performance Analytics

UVI measures every MLB player on a pitch-by-pitch basis, 
normalized across all 30 stadiums and positions. Every pitch 
thrown or seen contributes to a player's score, weighted by 
two simultaneous leverage factors: count context and win 
probability. The result is a park-neutralized performance 
score where 100 equals league average.

**Live app:** uvi-analytics.streamlit.app  
**Methodology:** charleshildbold.com/portfolio

---

## What's in this repo

- `app.py` — Streamlit application
- `uvi_engine.py` — Core calculation engine
- `update_2026_daily.py` — Daily data update script
- `pull_2026_components.py` — Sprint speed, OAA, running splits
- `daily_update.bat` — Windows batch file for daily updates

## Data

Data files are hosted on GitHub Releases v2.2.0 and downloaded 
automatically on first load. The app covers:

- **2025** — Full season, all 30 teams, 711,897 pitches
- **2026** — Live season, updated daily through last night's games

## Validation

- Hitters vs wOBA: r = +0.769 (n=308, 250+ PA)
- Starting Pitchers vs FIP: r = −0.807 (n=191, 50+ IP)
- Starting Pitchers vs ERA: r = −0.823 (n=191, 50+ IP)

## Built with

Python · Streamlit · Plotly · Pandas · Statcast · GitHub Actions

---

*Built by Charles Hildbold — charleshildbold.com*

# Changelog

---

## [2.1.0] — Phase 1 Release Candidate

### Added
- **Game Detail Panel** — select any game date on the trend chart to see a full
  box score inline. Shows traditional stats alongside the UVI score so any user
  can immediately understand what drove the number.
  - Pitchers: IP, K, BB, H, HR, R, pitch count, avg velocity
  - Hitters: AB/H, HR, RBI, BB/K, AVG, OPS, pitches seen, hard hit balls,
    avg exit velocity, xwOBA
- **Auto-generated game notes** in plain English (e.g. "dominant strikeout outing
  (11 K), perfect command — zero walks. UVI of 187.3 reflects this weighted by
  game leverage.")
- **Two-tier hitter reliability system** — data-derived from full 2025 season:
  - 10+ pitches = full reliability (gold dot) — standard 3–4 PA starter game
  - 6–9 pitches = partial game caution (dim grey dot)
  - Under 6 pitches = very limited sample (open grey circle)
  - Pitchers retain 15-pitch threshold

### Fixed
- Arizona Diamondbacks: Statcast uses `AZ` not `ARI` — no data was showing
- "Park Transfer" renamed "Stadium Effect" in Simulator
- Gauge chart margin conflict error
- Trend chart y-axis now scales to reliable games only
- Peak Game, Top 5, Bottom 5 filter to reliable games only
- Athletics renamed from "Oakland Athletics" to "Athletics"

### Changed
- Tier terminology updated to baseball-native language:
  Elite Apex → Impact Player · All-Star → Proven Starter ·
  Above Average → Solid Contributor · League Average → Roster Average ·
  Below Average → Fringe Roster · Value Leak → DFA Candidate

---

## [2.0.0] — Full League Engine Rebuild

### Added
- Full 2025 season, all 30 teams, 711,897 pitches from raw Statcast
- Leverage weighting: count leverage × win probability leverage
- Complete UVI: batting + speed + hustle + defense + burst components
- Daily auto-update script (pybaseball, no paid subscription)
- Season leaderboard, trend chart, monthly breakdown, simulator, methodology page

### Fixed
- Two-formula inconsistency causing different scores on each run
- Arbitrary 150 multiplier replaced with data-derived value
- Aggregation now sums raw values — never averages game UVIs
- Park factors applied to all historical scores

---

## [1.0.0] — Initial Build
- Basic UVI from game-level CSVs, PIT + BOS only, Streamlit app

# Contributing to UVI

---

## The One Rule That Cannot Break

**All UVI math lives in `uvi_engine.py`. Never put formulas anywhere else.**

If you find yourself writing a calculation in `app.py`, stop. Move it to the engine. This is what keeps scores consistent across every view, every run, every update.

---

## Formula Changes

Before changing anything in the UVI formula:

1. Document why the change improves accuracy
2. Run the validation check against known reference players
3. Note that changing LEAGUE_MEAN or MULTIPLIER re-scales all historical scores — this requires a CHANGELOG entry and a version bump

```bash
# Validation check
python validate_engine.py --player "Paul Skenes" --expected-tier "All-Star"
python validate_engine.py --player "Garrett Crochet" --expected-tier "All-Star"
```

---

## Adding New Data Sources

New Statcast columns go through the engine, not the app. Pattern:

```python
# In uvi_engine.py
def compute_game_uvi(df, role):
    # existing calculation
    df['new_component'] = df['new_column'] * WEIGHT
    df['uvi'] = df['raw_uvi'] + df['new_component']
    return df
```

---

## Daily Update Script

`update_data.py` appends to master CSVs. Rules:
- Never overwrite the master file — always append
- Always log what was pulled and the row count added
- If a game_pk already exists in the master file, skip it (deduplication)
- If pybaseball throws an error, log it and exit cleanly — do not corrupt the master file

---

## File Naming

| File | Purpose |
|------|---------|
| `app.py` | Display only |
| `uvi_engine.py` | All calculations |
| `update_data.py` | Daily Statcast pull |
| `validate_engine.py` | Regression tests for formula changes |
| `data/master_hitter_audit.csv` | Full league hitter game log — never delete rows |
| `data/master_pitcher_audit.csv` | Full league pitcher game log — never delete rows |

---

## Questions

Contact: Charles Hildbold

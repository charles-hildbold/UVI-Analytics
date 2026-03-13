# Unified Value Index (UVI) | MLB Performance Audit Engine

### *Redefining Player Worth through Situational Neutralization*

The **Unified Value Index (UVI)** is a proprietary performance metric designed to bridge the gap between traditional outcomes (box scores) and true player efficiency. While traditional metrics like WAR and OPS provide a snapshot of results, the UVI audits the **process** of every pitch, accounting for environmental context, leverage, and physical effort.

---

## 🚀 The Vision
In a 162-game season, "luck" and "environment" often mask a player's true trajectory. A home run in a hitter-friendly park during a blowout is mathematically different from a high-leverage walk in a pitcher's haven. The UVI was built to identify the **"Inside-Out"** worth of a player by neutralizing these variables.

---

## 🧠 The "Gears" of the UVI Engine

Everything in the UVI starts at a **Baseline of 100** (League Average). A player's score fluctuates pitch-by-pitch based on three core "Gears":

1.  **Gear 1: Discipline (The Mental Game):** Points are awarded or deducted based on count control. Winning a 3-2 battle or avoiding a 1-1 hole carries significant weight.
2.  **Gear 2: Impact (The Clutch Apex):** Using Win Probability Added (WPA) scaling, the UVI rewards players who perform when the game is on the line, while penalizing "Value Leaks" in high-leverage failures.
3.  **Gear 3: The Neutralizer (The Environment):** Scores are adjusted across all 30 MLB stadiums using a dynamic Park Factor dictionary. This ensures that a 120 UVI in Seattle (SEA) represents the same skill level as a 120 UVI in Colorado (COL).

---

## 🛠️ The Technical Implementation

The engine is built in **Python 3.x** and deployed via **Streamlit**. Below is the core logic used to neutralize player worth across the league:

```python
import pandas as pd

# Neutralization Dictionary (100 = Neutral)
PARK_FACTORS = {
    'COL': 131, 'MIA': 113, 'BOS': 109, 'PIT': 105, 'BAL': 100, 'SEA': 84
}

def apply_neutralization(raw_score, team_code, role):
    """
    Adjusts the final score based on the stadium factor.
    """
    pf = PARK_FACTORS.get(team_code, 100) / 100
    if role == 'Hitter':
        # If park is 109 (Hitter friendly), we divide to neutralize the 'boost'
        return raw_score / pf
    else:
        # If park is 109 (Harder for pitchers), we multiply to reward the effort
        return raw_score * pf

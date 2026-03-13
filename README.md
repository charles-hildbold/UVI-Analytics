Unified Value Index (UVI) | MLB Performance Audit Engine
Redefining Player Worth through Situational Neutralization
The Unified Value Index (UVI) is a proprietary performance metric designed to bridge the gap between traditional outcomes (box scores) and true player efficiency. While traditional metrics like WAR and OPS provide a snapshot of results, the UVI audits the process of every pitch, accounting for environmental context, leverage, and physical effort.

The Vision
In a 162-game season, "luck" and "environment" often mask a player's true trajectory. A home run in a hitter-friendly park during a blowout is mathematically different from a high-leverage walk in a pitcher's haven. The UVI was built to identify the "Inside-Out" worth of a player by neutralizing these variables.

How It Works (The Three Pillars)
Everything in the UVI starts at a Baseline of 100 (League Average). A player's score fluctuates pitch-by-pitch based on:

Plate Discipline (The Mental Game): Points are awarded or deducted based on count control. Falling behind 0-2 or winning a 3-2 battle carries significant weight.

Clutch Efficiency (The Impact Game): Using Win Probability Added (WPA) scaling, the UVI rewards players who "Apex" when the game is on the line, while penalizing "Value Leaks" in high-leverage failures.

The Environment (The Neutralizer): Scores are adjusted across all 30 MLB stadiums using a dynamic Park Factor dictionary. This ensures that a 120 UVI in Seattle (SEA) is equal in skill to a 120 UVI in Colorado (COL).

Tech Stack
Language: Python 3.x

Libraries: Pandas (Data manipulation), NumPy (Statistical modeling), Plotly (Data visualization)

Deployment: Streamlit (Mobile-responsive web interface)

Data Source: Statcast / Baseball Savant raw CSV exports

Key Terminology
Clutch Apex: A high-leverage event that significantly increases team win probability.

Liability Leak: A situational failure where a player's worth drops below the professional baseline.

Effort Rating: A Statcast-integrated metric tracking sprint speed and defensive range consistency.

Neutralized Worth: The final UVI score after park and weather adjustments are applied.

2025 Case Studies
Paul Skenes (PIT): Demonstrated elite consistency with a 191.6 Neutralized UVI—nearly double the league average for efficiency per pitch.

Ceddanne Rafaela (BOS): Showcased the "Safety Net" effect, where elite defensive range (OAA) maintained his value despite offensive volatility.

Garrett Crochet (BOS): Emerged as the "Gold Standard" for pitching efficiency, maintaining a 128.1 UVI in the demanding environment of Fenway Park.

Using the App
You can audit any player or game from the 2025 season using the live dashboard.

Select Team to load the roster.

Toggle between Historical Audit (Season Review) and Predictive Model (Live Scenarios).

Search Player to view their Scorecard, Effort Rating, and custom 'Scout AI' summary.

Contact & Development
Developed by Charles "Charlie" Hildbold, Data Analytics (M.S.).

"""
uvi_engine.py  —  Single source of truth for ALL UVI calculations.
No math lives anywhere else. app.py is display only.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import urllib.request
import os

# ── FROZEN CONSTANTS (2025 full-season, all 30 teams) ──────────────────────
P_MEAN: float = -0.01680715
P_MULT: float =  4723.5424
H_MEAN: float =  0.01343597
H_MULT: float =  3921.8597

LEAGUE_AVG_SPEED: float = 27.3204
LEAGUE_AVG_BURST: float =  2.5785
LEAGUE_AVG_HS:    float = 94.3784
LEAGUE_STD_HS:    float =  7.0331
# Reliability thresholds
MIN_PITCH_PITCHER:       int = 15  # pitchers: short outings are small sample
MIN_PITCH_HITTER_FULL:   int = 10  # hitters: 10+ pitches = reliable (3-4 PA starter)
MIN_PITCH_HITTER_PARTIAL: int = 6  # hitters: 6-9 pitches = partial game, soft caution
MIN_PITCH_RELIABILITY:   int = 10  # default fallback

# ── PARK FACTORS ───────────────────────────────────────────────────────────
PARK_FACTORS: dict = {
    'COL':1.15,'BOS':1.07,'CIN':1.06,'PHI':1.05,'TEX':1.04,
    'CHC':1.03,'NYY':1.03,'MIL':1.02,'HOU':1.01,'ATL':1.01,
    'AZ':1.00,'LAD':1.00,'STL':1.00,'TOR':1.00,'MIN':1.00,
    'DET':0.99,'CLE':0.99,'WSH':0.99,'KC':0.98,'ATH':0.98,
    'NYM':0.98,'LAA':0.97,'CWS':0.97,'TB':0.96,'SD':0.96,
    'SF':0.95,'BAL':0.95,'PIT':0.94,'MIA':0.93,'SEA':0.91,
}

TEAM_NAMES: dict = {
    'AZ':'Arizona Diamondbacks','ATL':'Atlanta Braves',
    'BAL':'Baltimore Orioles','BOS':'Boston Red Sox',
    'CHC':'Chicago Cubs','CWS':'Chicago White Sox',
    'CIN':'Cincinnati Reds','CLE':'Cleveland Guardians',
    'COL':'Colorado Rockies','DET':'Detroit Tigers',
    'HOU':'Houston Astros','KC':'Kansas City Royals',
    'LAA':'Los Angeles Angels','LAD':'Los Angeles Dodgers',
    'MIA':'Miami Marlins','MIL':'Milwaukee Brewers',
    'MIN':'Minnesota Twins','NYM':'New York Mets',
    'NYY':'New York Yankees','ATH':'Athletics',
    'PHI':'Philadelphia Phillies','PIT':'Pittsburgh Pirates',
    'SD':'San Diego Padres','SEA':'Seattle Mariners',
    'SF':'San Francisco Giants','STL':'St. Louis Cardinals',
    'TB':'Tampa Bay Rays','TEX':'Texas Rangers',
    'TOR':'Toronto Blue Jays','WSH':'Washington Nationals',
}

# ── TIERS ──────────────────────────────────────────────────────────────────
# Baseball-native language — terms a scout or GM would actually use
def uvi_tier(score: float) -> tuple:
    if score >= 160: return "Impact Player",    "#C9A84C"
    if score >= 130: return "Proven Starter",   "#52BE80"
    if score >= 115: return "Solid Contributor","#5DADE2"
    if score >= 90:  return "Roster Average",   "#AAB7B8"
    if score >= 70:  return "Fringe Roster",    "#E67E22"
    return                   "DFA Candidate",   "#E74C3C"

def uvi_emoji(score: float) -> str:
    if score >= 160: return "🔥"
    if score >= 130: return "⭐"
    if score >= 115: return "📈"
    if score >= 90:  return "⚾"
    if score >= 70:  return "📉"
    return "⚠️"

# ── CORE CALCULATIONS ──────────────────────────────────────────────────────
def compute_span_uvi(df: pd.DataFrame, role: str) -> float:
    total_shift   = df['shift'].sum()
    total_pitches = df['pitch_count'].sum()
    if total_pitches == 0:
        return 100.0
    mean = H_MEAN if role == 'hitter' else P_MEAN
    mult = H_MULT if role == 'hitter' else P_MULT
    raw  = 100.0 + (total_shift / total_pitches - mean) * mult
    team = df['team_tag'].mode().iloc[0] if not df.empty else 'ARI'
    pf   = PARK_FACTORS.get(str(team), 1.0)
    return float(raw / pf if role == 'hitter' else raw * pf)

def compute_game_uvi_col(df: pd.DataFrame, role: str) -> pd.Series:
    mean = H_MEAN if role == 'hitter' else P_MEAN
    mult = H_MULT if role == 'hitter' else P_MULT
    spp  = df['shift'] / df['pitch_count'].replace(0, np.nan)
    raw  = 100.0 + (spp - mean) * mult
    pf   = df['team_tag'].map(PARK_FACTORS).fillna(1.0)
    return (raw / pf if role == 'hitter' else raw * pf).round(1)

def compute_rolling_uvi(df: pd.DataFrame, role: str, window: int = 7) -> pd.DataFrame:
    df   = df.sort_values('game_date').copy()
    mean = H_MEAN if role == 'hitter' else P_MEAN
    mult = H_MULT if role == 'hitter' else P_MULT
    rs   = df['shift'].rolling(window, min_periods=1).sum()
    rp   = df['pitch_count'].rolling(window, min_periods=1).sum()
    raw  = 100.0 + (rs / rp - mean) * mult
    pf   = df['team_tag'].map(PARK_FACTORS).fillna(1.0)
    df['rolling_uvi'] = (raw / pf if role == 'hitter' else raw * pf).round(1)
    df['game_uvi']    = compute_game_uvi_col(df, role)
    # Two-tier reliability for hitters, single threshold for pitchers
    if role == 'hitter':
        df['reliable'] = df['pitch_count'] >= MIN_PITCH_HITTER_FULL
        df['reliability_level'] = 'low'
        df.loc[df['pitch_count'] >= MIN_PITCH_HITTER_PARTIAL, 'reliability_level'] = 'partial'
        df.loc[df['pitch_count'] >= MIN_PITCH_HITTER_FULL,    'reliability_level'] = 'full'
    else:
        df['reliable'] = df['pitch_count'] >= MIN_PITCH_PITCHER
        df['reliability_level'] = df['reliable'].map({True:'full', False:'low'})
    return df

def get_player_games(games_df: pd.DataFrame, player: str, role: str) -> pd.DataFrame:
    df = games_df[games_df['player_name'] == player].copy()
    df = df.sort_values('game_date').reset_index(drop=True)
    df['game_uvi'] = compute_game_uvi_col(df, role)
    return df

def get_leaderboard(season_df: pd.DataFrame, role: str,
                    min_games: int = 5, team: str = 'All') -> pd.DataFrame:
    score_col = 'complete_uvi' if role == 'hitter' else 'season_uvi'
    df = season_df[season_df['games'] >= min_games].copy()
    if team != 'All':
        df = df[df['team_tag'] == team]
    df = df.sort_values(score_col, ascending=False).reset_index(drop=True)
    df['tier']  = df[score_col].apply(lambda x: uvi_tier(x)[0])
    df['color'] = df[score_col].apply(lambda x: uvi_tier(x)[1])
    df['emoji'] = df[score_col].apply(uvi_emoji)
    df.index   += 1
    return df

# ── DATA LOADING ───────────────────────────────────────────────────────────

# GitHub Release download URL — update this to your actual release URL after
# creating the release and uploading the 6 CSV files as assets.
# Format: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v2.1.0/
GITHUB_RELEASE_URL = "https://github.com/charles-hildbold/UVI-Analytics/releases/download/v2.1.0/"

DATA_FILES = [
    'master_hitter_games_2025.csv',
    'master_pitcher_games_2025.csv',
    'hitter_season_2025.csv',
    'pitcher_season_2025.csv',
    'hitter_game_stats_2025.csv',
    'pitcher_game_stats_2025.csv',
]

def ensure_data(data_dir: str = 'data') -> None:
    """
    Download any missing data files from GitHub Releases.
    Only downloads if the file doesn't already exist locally.
    This means local runs use local files; Streamlit Cloud downloads once per session.
    """
    base = Path(data_dir)
    base.mkdir(parents=True, exist_ok=True)

    for fname in DATA_FILES:
        fpath = base / fname
        if not fpath.exists():
            url = GITHUB_RELEASE_URL + fname
            print(f'Downloading {fname}...')
            try:
                urllib.request.urlretrieve(url, fpath)
                print(f'  ✓ {fname}')
            except Exception as e:
                raise RuntimeError(
                    f"Could not download {fname} from GitHub Releases.\n"
                    f"URL tried: {url}\n"
                    f"Error: {e}\n\n"
                    f"If running locally, place the CSV files in the data/ folder.\n"
                    f"If on Streamlit Cloud, check that the GitHub Release exists "
                    f"and the URL in uvi_engine.py is correct."
                )

def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df['game_date']   = pd.to_datetime(df['game_date'])
    df['month_label'] = df['game_date'].dt.strftime('%B %Y')
    df['month_sort']  = df['game_date'].dt.to_period('M').astype(str)
    return df

def load_data(data_dir: str = 'data') -> tuple:
    ensure_data(data_dir)
    base = Path(data_dir)
    hg = _parse_dates(pd.read_csv(base / 'master_hitter_games_2025.csv'))
    pg = _parse_dates(pd.read_csv(base / 'master_pitcher_games_2025.csv'))
    hs = pd.read_csv(base / 'hitter_season_2025.csv')
    ps = pd.read_csv(base / 'pitcher_season_2025.csv')
    return hg, pg, hs, ps

def load_game_stats(data_dir: str = 'data') -> tuple:
    """Load traditional box score stats. Returns (hitter_stats, pitcher_stats)."""
    ensure_data(data_dir)
    base = Path(data_dir)
    hgs = pd.read_csv(base / 'hitter_game_stats_2025.csv')
    pgs = pd.read_csv(base / 'pitcher_game_stats_2025.csv')
    hgs['game_date'] = pd.to_datetime(hgs['game_date'])
    pgs['game_date'] = pd.to_datetime(pgs['game_date'])
    return hgs, pgs

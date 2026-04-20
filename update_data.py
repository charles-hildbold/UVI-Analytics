"""
update_data.py
==============
Daily auto-update — pulls Statcast via pybaseball, appends to master CSVs.

Usage
-----
    python update_data.py                    # yesterday's games
    python update_data.py --date 2026-04-15  # specific date
    python update_data.py --full-season 2026 # full season backfill

Cron (Mac/Linux) — runs daily at 6 AM:
    0 6 * * * cd /path/to/uvi && python update_data.py >> logs/update.log 2>&1
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)

DATA_DIR    = Path('data')
HITTER_CSV  = DATA_DIR / 'master_hitter_games_2025.csv'
PITCHER_CSV = DATA_DIR / 'master_pitcher_games_2025.csv'

from uvi_engine import (
    H_MEAN, H_MULT, P_MEAN, P_MULT,
    PARK_FACTORS,
)

COUNT_LEV = {
    (0,0):1.0,(1,0):1.1,(0,1):1.1,(2,0):1.2,(1,1):1.1,(0,2):1.3,
    (3,0):0.9,(2,1):1.2,(1,2):1.4,(3,1):1.3,(2,2):1.5,(3,2):1.6
}

def pull(start: str, end: str) -> pd.DataFrame:
    from pybaseball import statcast
    log.info(f'Pulling {start} → {end}')
    df = statcast(start_dt=start, end_dt=end)
    log.info(f'  {len(df):,} pitches')
    return df

def process(raw: pd.DataFrame) -> tuple:
    raw = raw.copy()
    raw['game_date']    = pd.to_datetime(raw['game_date'])
    raw['pitcher_team'] = np.where(raw['inning_topbot']=='Top', raw['home_team'], raw['away_team'])
    raw['batter_team']  = np.where(raw['inning_topbot']=='Top', raw['away_team'], raw['home_team'])

    raw['count_lev'] = raw.apply(lambda r: COUNT_LEV.get((int(r['balls']),int(r['strikes'])),1.0), axis=1)
    raw['wp_lev']    = (raw['delta_home_win_exp'].abs()*10).clip(0.5,3.0)
    raw['leverage']  = raw['count_lev'] * raw['wp_lev']
    raw['w_pre']     = raw['delta_pitcher_run_exp'] * raw['leverage']
    raw['w_re']      = raw['delta_run_exp']          * raw['leverage']

    def norm(n):
        if ',' in str(n):
            p = str(n).split(', ')
            return p[1].strip() + ' ' + p[0].strip()
        return str(n)

    pit_g = raw.groupby(['player_name','game_date','game_pk','pitcher_team']).agg(
        shift=('w_pre','sum'), pitch_count=('pitch_number','count'),
    ).reset_index()
    pit_g['player_name']     = pit_g['player_name'].apply(norm)
    pit_g['game_date']       = pit_g['game_date'].dt.strftime('%Y-%m-%d')
    pit_g['global_mean_spp'] = round(P_MEAN,8)
    pit_g['global_mult']     = round(P_MULT,4)
    pit_g.rename(columns={'pitcher_team':'team_tag'}, inplace=True)

    bat_g = raw.groupby(['batter','game_date','game_pk','batter_team']).agg(
        shift=('w_re','sum'), pitch_count=('pitch_number','count'),
    ).reset_index()
    bat_g['game_date']       = bat_g['game_date'].dt.strftime('%Y-%m-%d')
    bat_g['global_mean_spp'] = round(H_MEAN,8)
    bat_g['global_mult']     = round(H_MULT,4)
    bat_g.rename(columns={'batter':'player_id','batter_team':'team_tag'}, inplace=True)
    bat_g['player_name'] = bat_g['player_id'].astype(str)

    return bat_g, pit_g

def append(new: pd.DataFrame, path: Path, role: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        master = pd.read_csv(path)
        existing = set(zip(master['player_name'].astype(str),
                           master['game_date'].astype(str),
                           master['game_pk'].astype(str)))
        new_rows = new[~new.apply(
            lambda r: (str(r['player_name']),str(r['game_date']),str(r['game_pk'])) in existing, axis=1)]
        if new_rows.empty:
            log.info(f'  {role}: no new rows')
            return 0
        pd.concat([master, new_rows], ignore_index=True).to_csv(path, index=False)
    else:
        new.to_csv(path, index=False)
        new_rows = new
    n = len(new_rows)
    log.info(f'  {role}: +{n:,} rows → {path}')
    return n

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date')
    parser.add_argument('--full-season', type=int)
    args = parser.parse_args()

    if args.full_season:
        start = f'{args.full_season}-03-20'
        end   = f'{args.full_season}-10-01'
    elif args.date:
        start = end = args.date
    else:
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        start = end = yesterday

    import time
    current = datetime.strptime(start, '%Y-%m-%d')
    end_dt  = datetime.strptime(end,   '%Y-%m-%d')
    h_total = p_total = 0

    while current <= end_dt:
        chunk_end = min(current + timedelta(days=13), end_dt)
        s = current.strftime('%Y-%m-%d')
        e = chunk_end.strftime('%Y-%m-%d')
        try:
            raw    = pull(s, e)
            raw    = raw.drop_duplicates(subset=['game_pk','at_bat_number','pitch_number'])
            bat_g, pit_g = process(raw)
            h_total += append(bat_g, HITTER_CSV,  'Hitters')
            p_total += append(pit_g, PITCHER_CSV, 'Pitchers')
        except Exception as ex:
            log.error(f'  Error {s}→{e}: {ex}')
        time.sleep(5)
        current = chunk_end + timedelta(days=1)

    log.info(f'Done — {h_total+p_total:,} total new rows')

if __name__ == '__main__':
    main()

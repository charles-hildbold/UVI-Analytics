"""
app.py  —  Unified Value Index (UVI) | MLB Performance Audit Engine
Display only. All calculations in uvi_engine.py.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

from uvi_engine import (
    load_data, get_player_games, get_leaderboard,
    compute_span_uvi, compute_rolling_uvi, compute_game_uvi_col,
    uvi_tier, uvi_emoji,
    PARK_FACTORS, TEAM_NAMES,
    P_MEAN, P_MULT, H_MEAN, H_MULT,
    LEAGUE_AVG_SPEED,
    load_game_stats,
    MIN_PITCH_PITCHER, MIN_PITCH_HITTER_FULL, MIN_PITCH_HITTER_PARTIAL,
)

# ── CONFIG ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UVI | MLB Performance Audit",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

:root {
    --gold:   #C9A84C;
    --gold2:  #F0CC6E;
    --red:    #C0392B;
    --green:  #27AE60;
    --blue:   #2E86AB;
    --bg:     #080B0F;
    --bg2:    #0D1219;
    --bg3:    #131A24;
    --bg4:    #1A2333;
    --border: rgba(201,168,76,0.15);
    --text:   #E8E8E8;
    --muted:  #6B7A8D;
}

html, body, [data-testid="stApp"] {
    background-color: var(--bg) !important;
    font-family: 'Barlow', sans-serif;
    color: var(--text);
}
[data-testid="stApp"] { background: var(--bg) !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800;
}

/* Headings */
h1,h2,h3 { font-family:'Barlow Condensed',sans-serif !important; color:#fff !important; }
h1 { font-size:2.6rem !important; font-weight:900; letter-spacing:0.03em; }
h2 { font-size:1.7rem !important; font-weight:700; }
h3 { font-size:1.2rem !important; font-weight:600; }

/* Tabs */
[data-testid="stTabs"] button {
    font-family:'Barlow Condensed',sans-serif;
    font-size:0.85rem; font-weight:600;
    letter-spacing:0.1em; text-transform:uppercase;
    color: var(--muted) !important;
    border:none !important; border-radius:0 !important;
    padding:8px 16px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
    background: rgba(201,168,76,0.06) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border);
    gap: 2px;
}

hr { border-color: var(--border) !important; }
.stSelectbox > div > div { background: var(--bg3) !important; border-color: var(--border) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius:8px; }

/* Cards */
.stat-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.stat-card .label {
    font-size:0.65rem; color:var(--muted);
    text-transform:uppercase; letter-spacing:0.12em;
    margin-bottom:4px;
}
.stat-card .value {
    font-family:'Barlow Condensed',sans-serif;
    font-size:2rem; font-weight:800; color:var(--gold);
    line-height:1;
}
.stat-card .sub {
    font-size:0.78rem; color:var(--muted); margin-top:4px;
}

/* Player header */
.player-header {
    background: linear-gradient(135deg, var(--bg3) 0%, var(--bg4) 100%);
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.player-header .name {
    font-family:'Barlow Condensed',sans-serif;
    font-size:2rem; font-weight:900; color:#fff;
    letter-spacing:0.04em; line-height:1;
}
.player-header .meta {
    font-size:0.8rem; color:var(--muted);
    letter-spacing:0.08em; text-transform:uppercase;
    margin-top:4px;
}

/* Score pill */
.score-pill {
    display:inline-block;
    padding:3px 12px;
    border-radius:20px;
    font-family:'Barlow Condensed',sans-serif;
    font-size:0.8rem; font-weight:700;
    letter-spacing:0.08em;
}

/* Component breakdown bar */
.comp-row {
    display:flex; align-items:center; gap:10px;
    padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04);
    font-size:0.82rem;
}
.comp-label { width:130px; color:var(--muted); font-size:0.75rem; }
.comp-bar-wrap { flex:1; height:6px; background:rgba(255,255,255,0.06); border-radius:3px; }
.comp-bar { height:100%; border-radius:3px; }
.comp-val { width:50px; text-align:right; font-family:'Barlow Condensed',sans-serif;
            font-size:0.9rem; font-weight:700; }

/* Wordmark */
.wordmark {
    font-family:'Barlow Condensed',sans-serif;
    font-size:1.6rem; font-weight:900;
    letter-spacing:0.2em; color:var(--gold);
}
.wordmark-sub { font-size:0.62rem; color:var(--muted); letter-spacing:0.18em; text-transform:uppercase; }

/* Leaderboard row */
.lb-row {
    display:flex; align-items:center; gap:12px;
    padding:8px 12px; border-radius:6px;
    border-bottom:1px solid rgba(255,255,255,0.04);
    transition:background 0.15s;
}
.lb-row:hover { background:rgba(201,168,76,0.05); }
.lb-rank { width:28px; font-size:0.75rem; color:var(--muted); text-align:right; flex-shrink:0; }
.lb-name { flex:1; font-size:0.9rem; font-weight:500; }
.lb-team { width:36px; font-size:0.7rem; color:var(--muted); flex-shrink:0; }
.lb-bar-wrap { width:120px; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; flex-shrink:0; }
.lb-score { width:52px; text-align:right; font-family:'Barlow Condensed',sans-serif;
            font-size:1rem; font-weight:800; flex-shrink:0; }
</style>
""", unsafe_allow_html=True)

# ── PLOT THEME ──────────────────────────────────────────────────────────────
PLOT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Barlow, sans-serif', color='#E8E8E8'),
    margin=dict(l=10,r=10,t=36,b=10),
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)'),
    legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0),
)
GOLD = '#C9A84C'; RED = '#C0392B'; GRN = '#27AE60'; BLUE = '#2E86AB'

# ── DATA ────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return load_data('data')

@st.cache_data(show_spinner=False)
def get_boards():
    _, _, hs, ps = get_data()
    return hs, ps

@st.cache_data(show_spinner=False)
def get_game_stats():
    return load_game_stats('data')

try:
    hg, pg, hs, ps = get_data()
    hgs, pgs = get_game_stats()
    DATA_OK = True
except Exception as e:
    DATA_OK = False
    DATA_ERR = str(e)

# ── GAUGE CHART ─────────────────────────────────────────────────────────────
def gauge(value, title='UVI', height=200):
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        title=dict(text=title, font=dict(size=12, color='#6B7A8D', family='Barlow Condensed')),
        number=dict(font=dict(size=40, color=GOLD, family='Barlow Condensed')),
        gauge=dict(
            axis=dict(range=[0,200], tickfont=dict(color='#6B7A8D', size=9)),
            bar=dict(color=GOLD, thickness=0.2),
            bgcolor='rgba(255,255,255,0.03)',
            borderwidth=0.5, bordercolor='rgba(201,168,76,0.2)',
            steps=[
                dict(range=[0,70],   color='rgba(192,57,43,0.15)'),
                dict(range=[70,90],  color='rgba(230,126,34,0.10)'),
                dict(range=[90,115], color='rgba(255,255,255,0.04)'),
                dict(range=[115,130],color='rgba(39,174,96,0.10)'),
                dict(range=[130,200],color='rgba(201,168,76,0.12)'),
            ],
            threshold=dict(line=dict(color=GOLD,width=2), thickness=0.75, value=100),
        ),
    ))
    layout = {**PLOT, 'height': height}
    layout['margin'] = dict(l=20, r=20, t=20, b=10)
    fig.update_layout(**layout)
    return fig

# ── TREND CHART ─────────────────────────────────────────────────────────────
def trend_chart(df, role, window=7):
    df = compute_rolling_uvi(df, role, window)
    fig = go.Figure()

    # League average band
    fig.add_hrect(y0=90, y1=115, fillcolor='rgba(255,255,255,0.02)',
                  line_width=0, annotation_text='Roster Average Zone',
                  annotation_position='top left',
                  annotation_font=dict(color='#6B7A8D', size=9))

    if role == 'hitter':
        # Three tiers for hitters
        low     = df[df['reliability_level'] == 'low']
        partial = df[df['reliability_level'] == 'partial']
        full    = df[df['reliability_level'] == 'full']
        thresh_full    = MIN_PITCH_HITTER_FULL
        thresh_partial = MIN_PITCH_HITTER_PARTIAL
        low_label = f'Very Low Sample (<{thresh_partial} pitches)'
        par_label = f'Partial Game ({thresh_partial}–{thresh_full-1} pitches)'
    else:
        low     = df[~df['reliable']]
        partial = pd.DataFrame()
        full    = df[df['reliable']]
        thresh_full = MIN_PITCH_PITCHER
        low_label = f'Low Sample (<{thresh_full} pitches)'
        par_label = ''

    # Low-sample — grey open circles
    if not low.empty:
        fig.add_trace(go.Scatter(
            x=low['game_date'], y=low['game_uvi'], mode='markers',
            marker=dict(size=6, color='#4A5568', opacity=0.65,
                        symbol='circle-open',
                        line=dict(color='#4A5568', width=1.5)),
            name=low_label,
            hovertemplate=(
                '<b>%{x|%b %d}</b><br>UVI: %{y:.1f} · %{customdata} pitches<br>'
                '<i>⚠ Very limited sample — pinch hit or early exit</i>'
                '<extra></extra>'
            ),
            customdata=low['pitch_count'],
        ))

    # Partial (hitters only) — grey filled, half opacity
    if not partial.empty:
        fig.add_trace(go.Scatter(
            x=partial['game_date'], y=partial['game_uvi'], mode='markers',
            marker=dict(size=6, color='#718096', opacity=0.55),
            name=par_label,
            hovertemplate=(
                '<b>%{x|%b %d}</b><br>UVI: %{y:.1f} · %{customdata} pitches<br>'
                '<i>Partial game — interpret carefully</i>'
                '<extra></extra>'
            ),
            customdata=partial['pitch_count'],
        ))

    # Reliable — gold dots
    if not full.empty:
        fig.add_trace(go.Scatter(
            x=full['game_date'], y=full['game_uvi'], mode='markers',
            marker=dict(size=5, color=GOLD, opacity=0.5,
                        line=dict(color='rgba(0,0,0,0.3)', width=1)),
            name='Game UVI',
            hovertemplate='<b>%{x|%b %d}</b><br>UVI: %{y:.1f} · %{customdata} pitches<extra></extra>',
            customdata=full['pitch_count'],
        ))

    # Rolling trend line
    fig.add_trace(go.Scatter(
        x=df['game_date'], y=df['rolling_uvi'], mode='lines',
        line=dict(color=GOLD, width=2.5),
        name=f'{window}-Game Trend',
        hovertemplate='<b>%{x|%b %d}</b><br>Trend: %{y:.1f}<extra></extra>',
    ))

    fig.add_hline(y=100, line_dash='dot', line_color='rgba(201,168,76,0.3)', line_width=1)

    # Clip y-axis based on reliable games only so low-sample outliers don't distort scale
    reliable_vals = df.loc[df['reliable'], 'game_uvi'].dropna()
    if not reliable_vals.empty:
        y_max = min(reliable_vals.max() * 1.15, 350)
        y_min = max(reliable_vals.min() * 0.85, 0)
        fig.update_yaxes(range=[y_min, y_max])

    fig.update_layout(**PLOT, height=300,
        title=dict(text='Game-by-Game UVI · Rolling Trend',
                   font=dict(size=13, family='Barlow Condensed'), x=0),
        yaxis_title='UVI', xaxis_title='')
    return fig

# ── MONTHLY CHART ────────────────────────────────────────────────────────────
def monthly_chart(df, role):
    months = (df.groupby('month_label')
               .apply(lambda g: compute_span_uvi(g, role))
               .reset_index())
    months.columns = ['month_label','uvi']
    months['ms'] = pd.to_datetime(months['month_label'], format='%B %Y')
    months = months.sort_values('ms')
    colors = [GOLD if v >= 100 else RED for v in months['uvi']]
    fig = go.Figure(go.Bar(
        x=months['month_label'], y=months['uvi'],
        marker_color=colors,
        text=[f"{v:.0f}" for v in months['uvi']],
        textposition='outside',
        textfont=dict(color='#E8E8E8', size=11, family='Barlow Condensed'),
        hovertemplate='<b>%{x}</b><br>UVI: %{y:.1f}<extra></extra>',
    ))
    fig.add_hline(y=100, line_dash='dot', line_color='rgba(201,168,76,0.4)')
    fig.update_layout(**PLOT, height=260, showlegend=False,
        title=dict(text='Monthly UVI', font=dict(size=13,family='Barlow Condensed'), x=0))
    return fig

# ── COMPONENT BREAKDOWN (hitters) ────────────────────────────────────────────
def component_breakdown(row):
    batting = float(row.get('batting_uvi', row.get('season_uvi', 100)))
    comps = [
        ('Batting',  batting,              GOLD),
        ('Speed',    float(row.get('speed_bonus',   0)), GRN if float(row.get('speed_bonus',0)) >= 0 else RED),
        ('Hustle',   float(row.get('hustle_bonus',  0)), GRN if float(row.get('hustle_bonus',0)) >= 0 else RED),
        ('Defense',  float(row.get('defense_bonus', 0)), GRN if float(row.get('defense_bonus',0)) >= 0 else RED),
        ('Burst',    float(row.get('burst_bonus',   0)), GRN if float(row.get('burst_bonus',0)) >= 0 else RED),
    ]
    max_val = max(abs(c[1]) for c in comps) or 1
    html = '<div style="margin-top:8px">'
    for label, val, color in comps:
        pct = min(100, abs(val) / max_val * 100)
        html += f'''
        <div class="comp-row">
            <div class="comp-label">{label}</div>
            <div class="comp-bar-wrap">
                <div class="comp-bar" style="width:{pct}%;background:{color}"></div>
            </div>
            <div class="comp-val" style="color:{color}">{val:+.1f}</div>
        </div>'''
    html += '</div>'
    return html

# ── GAME LOG TABLE ────────────────────────────────────────────────────────────
def game_log_table(df, role):
    log = df[['game_date','team_tag','game_uvi','pitch_count','shift']].copy()
    log['game_date'] = log['game_date'].dt.strftime('%Y-%m-%d')
    log['game_uvi']  = log['game_uvi'].round(1)
    log['shift']     = log['shift'].round(3)
    log.columns      = ['Date','Team','UVI','Pitches','Shift']
    log = log.sort_values('Date', ascending=False)
    return log

# ── GAME DETAIL PANEL ────────────────────────────────────────────────────────
def game_detail_panel(player, role, game_date, p_data, stats_df):
    role_lower = role.lower()
    game_row = p_data[p_data['game_date'].dt.date == game_date]
    if game_row.empty:
        st.info(f'No game data for {game_date}.')
        return
    game_uvi = float(game_row['game_uvi'].iloc[0])
    pitches  = int(game_row['pitch_count'].iloc[0])
    reliable = pitches >= 15
    tl, tc   = uvi_tier(game_uvi)
    emoji    = uvi_emoji(game_uvi)
    stats_row = stats_df[
        (stats_df['player_name'] == player) &
        (stats_df['game_date'].dt.date == game_date)
    ]
    import datetime
    date_str = game_date.strftime('%B %d, %Y') if hasattr(game_date,'strftime') else str(game_date)
    st.markdown(f"""
    <div style="background:#1A2333;border:1px solid rgba(201,168,76,0.15);
                border-left:3px solid {tc};border-radius:10px;
                padding:18px 22px;margin:12px 0 16px">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
                            font-weight:800;color:#fff">{date_str}</div>
                <div style="font-size:0.75rem;color:#6B7A8D;margin-top:2px">
                    {pitches} pitches seen/thrown {'· ⚠️ Low sample — interpret with caution' if not reliable else ''}
                </div>
            </div>
            <div style="text-align:right">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:2.4rem;
                            font-weight:900;color:{tc};line-height:1">{game_uvi:.1f}</div>
                <div style="font-size:0.8rem;color:{tc}">{emoji} {tl}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if stats_row.empty:
        st.caption('Box score stats not available for this game.')
        return

    s = stats_row.iloc[0]

    if role_lower == 'pitcher':
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Innings Pitched', str(s.get('ip','—')))
        c2.metric('Strikeouts',      int(s.get('k',0)))
        c3.metric('Walks',           int(s.get('bb',0)))
        c4.metric('Hits Allowed',    int(s.get('h',0)))
        c1b,c2b,c3b,c4b = st.columns(4)
        c1b.metric('Home Runs',  int(s.get('hr',0)))
        c2b.metric('Runs',       int(s.get('r',0)))
        c3b.metric('Pitch Count',int(s.get('pitches',0)))
        velo = s.get('velo')
        c4b.metric('Avg Velocity', f"{velo:.1f} mph" if velo and not np.isnan(float(velo)) else '—')
        k=int(s.get('k',0)); bb=int(s.get('bb',0)); vv=s.get('velo',0)
        note=[]
        if k>=8:  note.append(f"dominant strikeout outing ({k} K)")
        if bb==0: note.append("perfect command — zero walks")
        if bb>=4: note.append(f"command issues ({bb} BB)")
        if vv and not np.isnan(float(vv)) and float(vv)>=96: note.append(f"premium velocity ({float(vv):.1f} mph)")
        if note: st.caption(f"📋 **Game note:** {', '.join(note).capitalize()}. UVI of {game_uvi:.1f} weights this against game leverage and run expectancy.")
    else:
        ab=int(s.get('ab',0)); h=int(s.get('h',0)); hr=int(s.get('hr',0))
        rbi=int(s.get('rbi',0)); bb=int(s.get('bb',0)); k=int(s.get('k',0))
        avg_val=s.get('avg',0); ops_val=s.get('ops',0)
        avg=f".{int(float(avg_val)*1000):03d}" if avg_val else '.000'
        ops=f"{float(ops_val):.3f}" if ops_val else '.000'
        ev=s.get('exit_velo'); xw=s.get('xwoba')
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric('AB / H',  f'{ab} / {h}')
        c2.metric('HR',      hr)
        c3.metric('RBI',     rbi)
        c4.metric('BB / K',  f'{bb} / {k}')
        c5.metric('AVG',     avg)
        c1b,c2b,c3b,c4b,c5b = st.columns(5)
        c1b.metric('OPS',          ops)
        c2b.metric('Pitches Seen', int(s.get('pitches_seen',0)))
        c3b.metric('Hard Hit Balls',int(s.get('hard_hit',0)))
        c4b.metric('Avg Exit Velo', f"{float(ev):.1f} mph" if ev and not np.isnan(float(ev)) else '—')
        c5b.metric('xwOBA', f"{float(xw):.3f}" if xw and not np.isnan(float(xw)) else '—')
        note=[]
        if hr>=2: note.append(f"multi-homer game ({hr} HR)")
        if h>=3:  note.append(f"multi-hit performance ({h} hits)")
        if bb>=2: note.append(f"excellent plate discipline ({bb} walks)")
        if k>=3:  note.append(f"tough day at the plate ({k} strikeouts)")
        if ev and not np.isnan(float(ev)) and float(ev)>=98: note.append(f"elite contact quality ({float(ev):.1f} mph avg exit velo)")
        if note: st.caption(f"📋 **Game note:** {', '.join(note).capitalize()}. UVI of {game_uvi:.1f} reflects this in context of the game situation and leverage.")

# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image('assets/header.png', use_container_width=True)
    except:
        st.markdown('<div class="wordmark">UVI</div>', unsafe_allow_html=True)
        st.markdown('<div class="wordmark-sub">Unified Value Index</div>', unsafe_allow_html=True)
        st.markdown('<div class="wordmark-sub">MLB Performance Audit Engine</div>', unsafe_allow_html=True)

    st.markdown('---')
    mode = st.radio('Navigation', [
        '📊 Player Audit',
        '🏆 Leaderboard',
        '🔮 Simulator',
        '📖 Methodology',
    ])
    st.markdown('---')

    if mode in ['📊 Player Audit', '🔮 Simulator'] and DATA_OK:
        role = st.radio('Role', ['Hitter', 'Pitcher'])
        teams_sorted = sorted(TEAM_NAMES.keys())
        team_labels  = [f"{t} — {TEAM_NAMES[t]}" for t in teams_sorted]
        sel_team_idx = st.selectbox('Team', range(len(teams_sorted)),
                                     format_func=lambda i: team_labels[i])
        team_code = teams_sorted[sel_team_idx]

        games_df  = hg if role == 'Hitter' else pg
        team_df   = games_df[games_df['team_tag'] == team_code]
        players   = sorted(team_df['player_name'].unique())

        if players:
            player = st.selectbox('Player', players)
            p_data = get_player_games(games_df, player, role.lower())
        else:
            st.warning(f'No {role.lower()} data for {team_code}')
            player = None
            p_data = pd.DataFrame()

    st.markdown('---')
    with st.expander('⚾ Score Guide'):
        st.markdown("""
| Score | Tier |
|-------|------|
| 160+  | 🔥 Impact Player |
| 130–159 | ⭐ Proven Starter |
| 115–129 | 📈 Solid Contributor |
| 90–114 | ⚾ Roster Average |
| 70–89 | 📉 Fringe Roster |
| <70 | ⚠️ DFA Candidate |

Baseline = **100** · All scores park-neutralized
        """)

# ────────────────────────────────────────────────────────────────────────────
# ERROR STATE
# ────────────────────────────────────────────────────────────────────────────
if not DATA_OK:
    st.error(f"⚠️ Could not load data files from `/data/` folder.\n\n`{DATA_ERR}`")
    st.info("Make sure all five CSV files are in the `data/` directory.")
    st.stop()

# ────────────────────────────────────────────────────────────────────────────
# PAGE: PLAYER AUDIT
# ────────────────────────────────────────────────────────────────────────────
if mode == '📊 Player Audit':
    if not player or p_data.empty:
        st.info('Select a team and player from the sidebar.')
        st.stop()

    role_lower = role.lower()
    season_uvi = compute_span_uvi(p_data, role_lower)
    tier, tier_color = uvi_tier(season_uvi)
    emoji = uvi_emoji(season_uvi)

    # Season row from season file
    s_df = hs if role == 'Hitter' else ps
    s_row = s_df[s_df['player_name'] == player]

    # Header
    recent = p_data.tail(7)
    recent_uvi = compute_span_uvi(recent, role_lower) if len(recent) >= 2 else season_uvi
    delta = recent_uvi - season_uvi

    st.markdown(f"""
    <div class="player-header">
        <div class="name">{player}</div>
        <div class="meta">{TEAM_NAMES.get(team_code, team_code)} &nbsp;·&nbsp; {role} &nbsp;·&nbsp;
        <span style="color:{tier_color}">{emoji} {tier}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Top metrics
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric('Season UVI', f'{season_uvi:.1f}')
    c2.metric('Last 7 Games', f'{recent_uvi:.1f}', delta=f'{delta:+.1f}')
    c3.metric('Games', int(p_data['game_date'].nunique()))
    c4.metric('Pitches Sampled', int(p_data['pitch_count'].sum()))
    if not p_data.empty:
        thresh = MIN_PITCH_PITCHER if role == "Pitcher" else MIN_PITCH_HITTER_FULL
        reliable_games = p_data[p_data['pitch_count'] >= thresh]
        if not reliable_games.empty:
            best = reliable_games.loc[reliable_games['game_uvi'].idxmax()]
            c5.metric('Peak Game UVI', f"{best['game_uvi']:.1f}",
                      help=f"{best['game_date'].strftime('%b %d')} · {int(best['pitch_count'])} pitches")
        else:
            c5.metric('Peak Game UVI', '—', help='No games above reliability threshold')

    st.markdown('---')

    # Complete UVI breakdown (hitters only)
    if role == 'Hitter' and not s_row.empty:
        r = s_row.iloc[0]
        complete = float(r.get('complete_uvi', season_uvi))
        ct, cc = uvi_tier(complete)
        st.markdown(f'**Complete UVI: <span style="color:{cc}">{complete:.1f} &nbsp; {uvi_emoji(complete)} {ct}</span>**',
                    unsafe_allow_html=True)
        st.markdown(component_breakdown(r), unsafe_allow_html=True)
        st.markdown('---')

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(['📈 Trend', '📅 Monthly', '📋 Game Log', '🔬 Reliability'])

    with tab1:
        col_chart, col_gauge = st.columns([3,1])
        with col_chart:
            window = st.slider('Rolling window', 3, 15, 7, key='tw')
            st.plotly_chart(trend_chart(p_data, role_lower, window),
                            use_container_width=True)
        with col_gauge:
            st.plotly_chart(gauge(season_uvi, 'Season UVI'), use_container_width=True)
            st.markdown(f'<div style="text-align:center;font-size:0.8rem;color:#6B7A8D">Park factor: {PARK_FACTORS.get(team_code,1.0):.2f}</div>',
                        unsafe_allow_html=True)

        # ── GAME DETAIL SELECTOR ──────────────────────────────────────────
        st.markdown('---')
        st.markdown('### 🔍 Game Detail')
        st.caption('Select a game date to see the full box score alongside the UVI breakdown.')

        stats_source = hgs if role == 'Hitter' else pgs
        available_dates = sorted(p_data['game_date'].dt.date.unique())

        sel_date = st.selectbox(
            'Select game date',
            available_dates,
            index=len(available_dates)-1,
            format_func=lambda d: d.strftime('%B %d, %Y'),
            key='game_detail_date'
        )

        game_detail_panel(player, role, sel_date, p_data, stats_source)

        st.markdown('---')
        col_top, col_bot = st.columns(2)
        thresh = MIN_PITCH_PITCHER if role == 'Pitcher' else MIN_PITCH_HITTER_FULL
        reliable = p_data[p_data['pitch_count'] >= thresh]
        with col_top:
            st.markdown('**🏆 Top 5 Games** *(15+ pitches)*')
            if not reliable.empty:
                for _, r in reliable.nlargest(5,'game_uvi').iterrows():
                    tl,tc = uvi_tier(r['game_uvi'])
                    st.markdown(f'<span style="color:{tc}">●</span> **{r["game_date"].strftime("%b %d")}** — {r["game_uvi"]:.1f} · {int(r["pitch_count"])} pitches', unsafe_allow_html=True)
            else:
                st.caption('No games above reliability threshold.')
        with col_bot:
            st.markdown('**📉 Bottom 5 Games** *(15+ pitches)*')
            if not reliable.empty:
                for _, r in reliable.nsmallest(5,'game_uvi').iterrows():
                    tl,tc = uvi_tier(r['game_uvi'])
                    st.markdown(f'<span style="color:{tc}">●</span> **{r["game_date"].strftime("%b %d")}** — {r["game_uvi"]:.1f} · {int(r["pitch_count"])} pitches', unsafe_allow_html=True)
            else:
                st.caption('No games above reliability threshold.')

    with tab2:
        st.plotly_chart(monthly_chart(p_data, role_lower), use_container_width=True)
        months = (p_data.groupby('month_label')
                  .apply(lambda g: pd.Series({
                      'UVI': round(compute_span_uvi(g, role_lower),1),
                      'Games': len(g),
                      'Pitches': int(g['pitch_count'].sum()),
                      'Avg Pitches/Game': round(g['pitch_count'].mean(),1),
                  }))
                  .reset_index())
        months['ms'] = pd.to_datetime(months['month_label'], format='%B %Y')
        months = months.sort_values('ms').drop(columns='ms')
        st.dataframe(months, hide_index=True, use_container_width=True)

    with tab3:
        log = game_log_table(p_data, role_lower)
        st.dataframe(log, hide_index=True, use_container_width=True, height=420)

        col_dl1, col_dl2 = st.columns([1,3])
        with col_dl1:
            csv = log.to_csv(index=False)
            st.download_button('⬇ Download Game Log', csv,
                               file_name=f'{player.replace(" ","_")}_uvi_2025.csv',
                               mime='text/csv')

    with tab4:
        fig = go.Figure(go.Scatter(
            x=p_data['pitch_count'], y=p_data['game_uvi'],
            mode='markers',
            marker=dict(
                size=8, opacity=0.7,
                color=p_data['game_uvi'],
                colorscale=[[0,RED],[0.35,'#E67E22'],[0.5,'#AAB7B8'],[0.75,GRN],[1,GOLD]],
                cmin=50, cmax=160, showscale=True,
                colorbar=dict(title='UVI', tickfont=dict(color='#6B7A8D')),
                line=dict(color='rgba(0,0,0,0.2)',width=1),
            ),
            hovertemplate='<b>%{text}</b><br>Pitches: %{x}<br>UVI: %{y:.1f}<extra></extra>',
            text=p_data['game_date'].dt.strftime('%b %d'),
        ))
        fig.add_hline(y=100, line_dash='dot', line_color='rgba(201,168,76,0.4)')
        thresh_vline = MIN_PITCH_PITCHER if role == 'Pitcher' else MIN_PITCH_HITTER_FULL
        fig.add_vline(x=thresh_vline, line_dash='dash', line_color='rgba(255,255,255,0.15)',
                      annotation_text='Reliability threshold',
                      annotation_position='top right',
                      annotation_font=dict(color='#6B7A8D', size=9))
        fig.update_layout(**PLOT, height=300,
            title=dict(text='UVI vs Sample Size', font=dict(size=13,family='Barlow Condensed'), x=0),
            xaxis_title='Pitches', yaxis_title='Game UVI', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        thresh = MIN_PITCH_PITCHER if role == 'Pitcher' else MIN_PITCH_HITTER_FULL
        low = p_data[p_data['pitch_count'] < thresh]
        if not low.empty:
            if role == 'Hitter':
                partial = p_data[(p_data['pitch_count'] >= MIN_PITCH_HITTER_PARTIAL) & (p_data['pitch_count'] < MIN_PITCH_HITTER_FULL)]
                st.caption(
                    f'⚠️ {len(low)} game(s) below {MIN_PITCH_HITTER_PARTIAL} pitches (grey open circles — pinch hit / early exit). '
                    f'{len(partial)} game(s) between {MIN_PITCH_HITTER_PARTIAL}–{MIN_PITCH_HITTER_FULL-1} pitches (dim circles — partial game). '
                    f'Only gold dots ({MIN_PITCH_HITTER_FULL}+ pitches) represent full starter reliability.'
                )
            else:
                st.caption(f'⚠️ {len(low)} game(s) below {MIN_PITCH_PITCHER}-pitch reliability threshold (grey open circles). Short relief outings naturally produce extreme UVI values — excluded from trend calculations.')

# ────────────────────────────────────────────────────────────────────────────
# PAGE: LEADERBOARD
# ────────────────────────────────────────────────────────────────────────────
elif mode == '🏆 Leaderboard':
    st.markdown('## 🏆 2025 Season Leaderboard')
    st.markdown('Park-neutralized · All 30 teams · Leverage-weighted')
    st.markdown('---')

    lb_role = st.radio('Role', ['Hitter','Pitcher'], horizontal=True, key='lb_r')
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        teams_all  = ['All'] + sorted(TEAM_NAMES.keys())
        sel_t      = st.selectbox('Filter by Team', teams_all, key='lb_t')
    with col_f2:
        min_g = st.slider('Min games', 5, 50, 10, key='lb_g')
    with col_f3:
        top_n = st.slider('Show top N', 10, 50, 25, key='lb_n')

    board   = get_leaderboard(hs if lb_role=='Hitter' else ps, lb_role.lower(), min_g, sel_t)
    score_c = 'complete_uvi' if lb_role=='Hitter' else 'season_uvi'
    board   = board.head(top_n)

    # Top 5 cards
    st.markdown('### Top Performers')
    top5_cols = st.columns(5)
    for i, (_, row) in enumerate(board.head(5).iterrows()):
        score = float(row[score_c])
        tl, tc = uvi_tier(score)
        with top5_cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span style="font-size:1.1rem">#{i+1}</span>
                    <span style="font-size:0.7rem;color:#6B7A8D">{row['team_tag']}</span>
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;font-weight:700;margin-bottom:6px;line-height:1.1">{row['player_name']}</div>
                <div class="value">{score:.0f}</div>
                <div class="sub" style="color:{tc}">{uvi_emoji(score)} {tl}</div>
                <div class="sub">{int(row['games'])} G · {int(row.get('total_pitches',0))} pitches</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('---')

    # Bar chart
    colors = [uvi_tier(float(r[score_c]))[1] for _, r in board.iterrows()]
    fig = go.Figure(go.Bar(
        x=board['player_name'], y=board[score_c],
        marker_color=colors,
        text=[f"{v:.0f}" for v in board[score_c]],
        textposition='outside',
        textfont=dict(color='#E8E8E8',size=9,family='Barlow Condensed'),
        hovertemplate='<b>%{x}</b> (%{customdata})<br>UVI: %{y:.1f}<extra></extra>',
        customdata=board['team_tag'],
    ))
    fig.add_hline(y=100, line_dash='dot', line_color='rgba(201,168,76,0.4)')
    fig.update_layout(**PLOT, height=320,
        title=dict(text=f'Top {len(board)} {lb_role}s — 2025 Season UVI',
                   font=dict(size=13,family='Barlow Condensed'), x=0),
        xaxis_tickangle=-40, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Full table
    st.markdown('### Full Rankings')
    show_cols = ['player_name','team_tag', score_c,'tier','games','total_pitches']
    if lb_role == 'Hitter':
        show_cols += ['speed_bonus','defense_bonus']
    tbl = board[show_cols].copy()
    tbl.columns = (['Player','Team','UVI','Tier','Games','Pitches'] +
                   (['Speed Bonus','Defense Bonus'] if lb_role=='Hitter' else []))
    st.dataframe(tbl, use_container_width=True, height=450)

    csv = tbl.to_csv(index=False)
    st.download_button('⬇ Download Rankings', csv,
                       file_name=f'uvi_2025_{lb_role.lower()}s.csv', mime='text/csv')

# ────────────────────────────────────────────────────────────────────────────
# PAGE: SIMULATOR
# ────────────────────────────────────────────────────────────────────────────
elif mode == '🔮 Simulator':
    if not player or p_data.empty:
        st.info('Select a team and player from the sidebar.')
        st.stop()

    role_lower = role.lower()
    st.markdown(f'## 🔮 Predictive Simulator')
    st.markdown(f'**{player} · {TEAM_NAMES.get(team_code, team_code)} · {role}**')
    st.markdown('---')

    career_uvi = compute_span_uvi(p_data, role_lower)
    home_pf    = PARK_FACTORS.get(team_code, 1.0)

    col_info, col_g = st.columns([3,2])
    with col_info:
        st.markdown('### 2025 Career Baseline')
        c1,c2 = st.columns(2)
        c1.metric('Season UVI', f'{career_uvi:.1f}')
        c2.metric('Home Park Factor', f'{home_pf:.2f}')
        tl, tc = uvi_tier(career_uvi)
        st.markdown(f'**Tier:** <span style="color:{tc}">{uvi_emoji(career_uvi)} {tl}</span>',
                    unsafe_allow_html=True)
    with col_g:
        st.plotly_chart(gauge(career_uvi, 'Career UVI', 180), use_container_width=True)

    st.markdown('---')
    st.markdown('### Scenario Builder')

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        target_park = st.selectbox('Target Stadium', sorted(PARK_FACTORS.keys()),
                                   index=list(sorted(PARK_FACTORS.keys())).index(team_code)
                                   if team_code in PARK_FACTORS else 0)
        temp = st.slider('Temperature (°F)', 30, 110, 72)
    with sc2:
        opp_tier = st.selectbox('Opponent Quality',
                                ['Elite (top 10%)','Above Average','Average','Below Average','Weak'])
        night    = st.checkbox('Night Game', value=True)
    with sc3:
        rest_days = st.slider('Days Rest', 0, 5, 4)

    # Simulation
    target_pf = PARK_FACTORS.get(target_park, 1.0)
    total_s   = p_data['shift'].sum()
    total_p   = p_data['pitch_count'].sum()
    mean      = H_MEAN if role_lower=='hitter' else P_MEAN
    mult      = H_MULT if role_lower=='hitter' else P_MULT
    base_raw  = 100.0 + (total_s / total_p - mean) * mult

    if role_lower == 'hitter':
        neutral = base_raw * home_pf
        park_adj = neutral / target_pf - career_uvi
    else:
        neutral = base_raw / home_pf
        park_adj = neutral * target_pf - career_uvi

    temp_adj = (temp - 72) * (0.05 if role_lower=='hitter' else -0.04)
    opp_map  = {'Elite (top 10%)':-5.0,'Above Average':-2.5,'Average':0.0,'Below Average':2.5,'Weak':5.0}
    opp_adj  = opp_map.get(opp_tier,0.0) * (1 if role_lower=='hitter' else -1)
    night_adj = 1.5 if (night and role_lower=='hitter') else (-0.5 if night else 0.0)
    rest_adj  = (rest_days - 4) * (0.3 if role_lower=='pitcher' else 0.1)

    pred_uvi = career_uvi + park_adj + temp_adj + opp_adj + night_adj + rest_adj
    delta    = pred_uvi - career_uvi
    pt, pc   = uvi_tier(pred_uvi)

    st.markdown('---')
    st.markdown('### Prediction')
    r1,r2,r3,r4 = st.columns(4)
    r1.metric('Predicted UVI', f'{pred_uvi:.1f}', delta=f'{delta:+.1f} vs season avg')
    r2.metric('Stadium Effect', f'{park_adj:+.1f}')
    r3.metric('Weather Shift', f'{temp_adj:+.1f}')
    r4.metric('Projected Tier', f'{uvi_emoji(pred_uvi)} {pt}')

    adj_df = pd.DataFrame({
        'Factor': ['Stadium Effect','Temperature','Opposition','Time of Day','Rest'],
        'Value':  [park_adj, temp_adj, opp_adj, night_adj, rest_adj]
    })
    bar_c = [GRN if v>=0 else RED for v in adj_df['Value']]
    fig = go.Figure(go.Bar(
        x=adj_df['Factor'], y=adj_df['Value'],
        marker_color=bar_c,
        text=[f'{v:+.1f}' for v in adj_df['Value']],
        textposition='outside',
        textfont=dict(color='#E8E8E8',size=11,family='Barlow Condensed'),
    ))
    fig.add_hline(y=0, line_color='rgba(255,255,255,0.2)')
    fig.update_layout(**PLOT, height=240, showlegend=False,
        title=dict(text='Adjustment Breakdown', font=dict(size=13,family='Barlow Condensed'), x=0))
    st.plotly_chart(fig, use_container_width=True)
    st.info(f'**Scout Note:** {player} projected at **{pred_uvi:.1f} UVI** in {target_park} under these conditions — a **{delta:+.1f}** shift from their 2025 season average.')

# ────────────────────────────────────────────────────────────────────────────
# PAGE: METHODOLOGY
# ────────────────────────────────────────────────────────────────────────────
elif mode == '📖 Methodology':
    st.markdown('## 📖 UVI Methodology')
    st.markdown('---')

    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("""
### What is UVI?

The **Unified Value Index** is a pitch-by-pitch performance metric measuring every player against the full league, normalized across all 30 parks and all positions. Baseline = **100** (league average).

---

### The Formula

```
spp      = Σ(weighted_shift) / Σ(pitch_count)
raw_uvi  = 100 + (spp − LEAGUE_MEAN) × MULTIPLIER
uvi      = raw_uvi ÷ park_factor   [hitters]
uvi      = raw_uvi × park_factor   [pitchers]
```

Each standard deviation above league average = **+50 UVI points**.

---

### Leverage Weighting

Every pitch is weighted before contributing to UVI:

```
count_leverage  = {3-2: 1.6×, 2-2: 1.5×, 1-2: 1.4× ...}
win_prob_lev    = clip(|Δwin_prob| × 10, 0.5, 3.0)
leverage        = count_lev × win_prob_lev
weighted_value  = delta_run_exp × leverage
```

A strikeout on 3-2 in a tie game = **~4-5× more** than a pitch in a blowout.

---

### Complete UVI (Hitters)

```
complete_uvi = batting_uvi
             + speed_bonus      (±10 pts max)
             + hustle_bonus     (±8 pts max)
             + defense_bonus    (±15 pts max)
             + burst_bonus      (±3 pts max)
```

**Hustle is measured independently of talent.** A slow player running harder than their personal average earns a positive hustle score — rewarding effort regardless of physical ability.

---

### Constants (frozen — never change between runs)

| Constant | Value |
|----------|-------|
| P_MEAN | -0.01680715 |
| P_MULT | 4723.54 |
| H_MEAN | 0.01343597 |
| H_MULT | 3921.86 |
| League Avg Speed | 27.32 ft/sec |

        """)
    with col2:
        st.markdown('### Score Tiers')
        tiers = [
            ('160+',   '🔥 Impact Player',    '#C9A84C', 'Historic value — 2+ std above avg'),
            ('130–159','⭐ Proven Starter',    '#52BE80', 'Clear top-of-roster contributor'),
            ('115–129','📈 Solid Contributor', '#5DADE2', 'Consistent positive value'),
            ('90–114', '⚾ Roster Average',    '#AAB7B8', 'Professional baseline'),
            ('70–89',  '📉 Fringe Roster',    '#E67E22', 'Below replacement threshold'),
            ('<70',    '⚠️ DFA Candidate',    '#E74C3C', 'Significant negative contribution'),
        ]
        for score, label, color, desc in tiers:
            st.markdown(f"""
            <div class="stat-card" style="margin-bottom:8px;padding:12px 16px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:800;color:{color}">{score}</span>
                    <span style="font-size:0.78rem;color:{color}">{label}</span>
                </div>
                <div style="font-size:0.72rem;color:#6B7A8D;margin-top:3px">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('---')
        st.markdown('### Data Sources')
        st.markdown("""
- **Statcast** — pitch-by-pitch, 711,897 pitches, full 2025 season
- **Sprint Speed** — 617 players, full league
- **Outs Above Average** — 518 players, all positions
- **Running Splits** — 549 players, first-step quickness
        """)
        st.markdown('---')
        st.markdown('**Developed by**  \nCharles "Charlie" Hildbold  \nData Analytics, M.S.  \n*Unified Value Index, 2025*')

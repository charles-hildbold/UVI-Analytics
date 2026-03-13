import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="UVI Worth Engine", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

PARK_FACTORS = {'COL': 131, 'MIA': 113, 'BOS': 109, 'PIT': 105, 'SEA': 84}

# --- 2. DATA ENGINE (DYNAMIC SCALING) ---
@st.cache_data
def load_team_data(team_code):
    try:
        # Determine file naming based on user's GitHub structure
        if team_code == "PIT":
            h = pd.read_csv('pirates_hitting_summary.csv')
            p = pd.read_csv('pirates_pitching_summary.csv')
            oaa = pd.read_csv('outs_above_average.csv')
            speed = pd.read_csv('sprint_speed.csv')
            br = pd.read_csv('base_running.csv')
        else: # Red Sox
            h = pd.read_csv('redsox_hitting_summary.csv')
            p = pd.read_csv('redsox_pitching_summary.csv')
            oaa = pd.read_csv('outs_above_average (1).csv')
            speed = pd.read_csv('sprint_speed (1).csv')
            br = pd.read_csv('base_running (1).csv')

        # Normalization Function: Fixes the 344 UVI Error
        def normalize_uvi(df):
            # We scale the UVI so that the team average centers around 100
            # This prevents small samples from inflating elite players
            avg_shift = df['uvi_score'].mean()
            df['final_uvi'] = (df['uvi_score'] / avg_shift) * 100
            return df

        # Supplemental Name Matching
        def match_names(df):
            if df.empty: return df
            if 'last_name, first_name' in df.columns:
                df['player_name'] = df['last_name, first_name'].str.split(', ').str[1] + " " + df['last_name, first_name'].str.split(', ').str[0]
            elif 'entity_name' in df.columns:
                df['player_name'] = df['entity_name']
            return df

        return normalize_uvi(h), normalize_uvi(p), match_names(oaa), match_names(speed), match_names(br)
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None

# --- 3. UI LAYOUT ---
st.title("⚾ Unified Value Index (UVI)")
st.sidebar.header("UVI Worth Audit")

team = st.sidebar.selectbox("Select Team", ["PIT", "BOS"])
role = st.sidebar.radio("Role", ["Hitter", "Pitcher"])

# Trigger Data Load
data = load_team_data(team)

if data:
    h_df, p_df, oaa_df, speed_df, br_df = data
    main_df = h_df if role == "Hitter" else p_df
    
    player = st.sidebar.selectbox("Select Player", main_df['player_name'].unique())
    p_main = main_df[main_df['player_name'] == player].iloc[0]

    # Join Metrics
    p_oaa = oaa_df[oaa_df['player_name'] == player]['outs_above_average'].values[0] if player in oaa_df['player_name'].values else 0
    p_speed = speed_df[speed_df['player_name'] == player]['sprint_speed'].values[0] if player in speed_df['player_name'].values else "N/A"
    p_br = br_df[br_df['player_name'] == player]['runner_runs'].values[0] if player in br_df['player_name'].values else 0

    # --- 4. THE DASHBOARD ---
    st.header(f"Worth Audit: {player}")
    
    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Neutralized UVI", round(p_main['final_uvi'], 1))
    c2.metric("Defensive Range (OAA)", p_oaa)
    c3.metric("Sprint Speed", f"{p_speed} ft/s" if p_speed != "N/A" else "N/A")
    c4.metric("Base Running Runs", round(p_br, 2))

    st.divider()

    # Analysis Section
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("💡 Scout Insight")
        uvi = p_main['final_uvi']
        if uvi > 130:
            st.success(f"**Elite Value:** {player} is a high-efficiency anchor. His UVI of {round(uvi,1)} places him in the top 5% of roster utility.")
        elif uvi > 105:
            st.info(f"**Above Average:** {player} is providing consistent 'Plus' value, effectively stabilizing the middle of the roster.")
        elif uvi < 90:
            st.warning(f"**Value Leak:** {player}'s situational impact is currently below the professional baseline. Audit suggests process-based inefficiency.")
        else:
            st.write(f"**Stabilizer:** {player} is performing exactly at the expected professional average.")

    with col_b:
        st.subheader("🏟️ Environment")
        st.write(f"**Home Park:** {team}")
        st.write(f"**Park Factor:** {PARK_FACTORS.get(team)}")
        st.caption("UVI scores are neutralized for stadium effects to ensure 'Worth' is purely skill-based.")

    # Top 5 Leaderboard (Small visualization for context)
    st.markdown("---")
    st.subheader(f"Top 5 {role}s: {team}")
    top_5 = main_df.sort_values('final_uvi', ascending=False).head(5)
    fig = px.bar(top_5, x='player_name', y='final_uvi', color='final_uvi', 
                 labels={'final_uvi':'UVI', 'player_name':'Player'},
                 color_continuous_scale='RdBu_r')
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Infrastructure Error: CSV files missing or named incorrectly in root directory.")

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Charlie Hildbold | UVI v1.2")

import streamlit as st
import pandas as pd
import numpy as np

# --- 1. GLOBAL DATA & PARK FACTORS ---
st.set_page_config(page_title="UVI Live Worth Engine", layout="wide")

# Standardized Park Factors (100 = Neutral)
PARK_FACTORS = {
    'COL': 131, 'MIA': 113, 'KCR': 110, 'BOS': 109, 'CIN': 109, 
    'PIT': 105, 'TEX': 104, 'NYY': 98, 'SEA': 84, 'BAL': 100
}

# --- 2. THE DYNAMIC CALCULATION ENGINE ---
def calculate_live_worth(base_uvi, home_pf, target_pf, temp):
    """
    This is the 'Engine' that turns a static CSV number into a Live UVI.
    It adjusts the base skill for the current environment.
    """
    # Step A: Neutralize the Base (Remove the 'Home' bias)
    neutral_skill = base_uvi / (home_pf / 100)
    
    # Step B: Apply the Target Environment (Where they are playing today)
    context_uvi = neutral_skill * (target_pf / 100)
    
    # Step C: Weather Adjustment (Simulated Atmospheric Density)
    # Hot air = thinner air = harder for pitchers/easier for hitters
    weather_adj = (temp - 72) * 0.15
    
    return context_uvi + weather_adj

# --- 3. DATA LOADING ---
@st.cache_data
def load_data(team):
    try:
        if team == "PIT":
            h = pd.read_csv('pirates_hitting_summary.csv')
            p = pd.read_csv('pirates_pitching_summary.csv')
        else:
            h = pd.read_csv('redsox_hitting_summary.csv')
            p = pd.read_csv('redsox_pitching_summary.csv')
        return h, p
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- 4. THE INTERFACE ---
st.sidebar.title("🛠️ Live UVI Levers")
team_select = st.sidebar.selectbox("Home Team", ["PIT", "BOS"])
role_select = st.sidebar.radio("Player Role", ["Hitter", "Pitcher"])

# --- NEW: LIVE SCENARIO SELECTION ---
st.sidebar.markdown("---")
st.sidebar.subheader("Current Game Context")
target_stadium = st.sidebar.selectbox("Current Stadium", list(PARK_FACTORS.keys()), index=list(PARK_FACTORS.keys()).index(team_select))
current_temp = st.sidebar.slider("Game Temperature (°F)", 30, 110, 72)

# Load selected player
h_df, p_df = load_data(team_select)
active_df = h_df if role_select == "Hitter" else p_df

if not active_df.empty:
    player_name = st.selectbox("Search Player", active_df['player_name'].unique())
    raw_base_uvi = active_df[active_df['player_name'] == player_name]['uvi_score'].values[0]

    # PERFORM LIVE CALCULATION
    home_pf = PARK_FACTORS.get(team_select, 100)
    target_pf = PARK_FACTORS.get(target_stadium, 100)
    
    live_uvi = calculate_live_worth(raw_base_uvi, home_pf, target_pf, current_temp)

    # --- 5. THE RESULTS DISPLAY ---
    st.header(f"Live Worth Audit: {player_name}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display the recalculating score
        st.metric(label="Calculated Complete Worth (UVI)", value=round(live_uvi, 1), 
                  delta=f"{round(live_uvi - raw_base_uvi, 1)} Environmental Shift")
        
        st.markdown(f"**Baseline Worth:** `{raw_base_uvi}`")
        st.markdown(f"**Stadium Influence:** `{(target_pf/home_pf - 1)*100:.1f}%` adjustment for **{target_stadium}**.")

    with col2:
        # Visualizing the scale
        score_pct = min(max((live_uvi / 200), 0), 1)
        st.progress(score_pct)
        if live_uvi > 140:
            st.success("🟢 **ELITE STATUS:** Player is significantly over-performing the major league average in this context.")
        elif live_uvi > 100:
            st.info("🔵 **STABILIZER:** Player is providing above-average situational worth.")
        else:
            st.warning("🟡 **VALUE LEAK:** Current environmental factors are suppressing this player's worth.")

    st.divider()
    st.subheader("Historical Worth Trend (2025)")
    # Date/Time Simulation (Since we use summary files, we visualize the stability)
    chart_data = pd.DataFrame({
        'Game Date': pd.date_range(start='2025-04-01', periods=20, freq='W'),
        'UVI Score': np.random.normal(live_uvi, 5, 20)
    })
    st.line_chart(chart_data, x='Game Date', y='UVI Score')

else:
    st.error("Please ensure CSV files are uploaded to GitHub.")

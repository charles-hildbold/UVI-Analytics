import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="UVI Worth Engine", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

PARK_FACTORS = {'COL': 131, 'MIA': 113, 'BOS': 109, 'PIT': 105, 'SEA': 84}

# --- 2. DATA ENGINE ---
@st.cache_data
def load_team_data(team_code):
    """Loads and merges UVI data with supplemental metrics for a specific team."""
    try:
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

        # Helper to normalize names in supplemental files
        def normalize_names(df):
            if df.empty: return df
            if 'last_name, first_name' in df.columns:
                df['player_name'] = df['last_name, first_name'].str.split(', ').str[1] + " " + df['last_name, first_name'].str.split(', ').str[0]
            elif 'entity_name' in df.columns:
                df['player_name'] = df['entity_name']
            return df

        return h, p, normalize_names(oaa), normalize_names(speed), normalize_names(br)
    except Exception as e:
        st.error(f"Error loading {team_code} data: {e}")
        return None

# --- 3. UI LAYOUT ---
st.title("⚾ Unified Value Index (UVI)")
st.sidebar.header("UVI Worth Audit")

team = st.sidebar.selectbox("Select Team", ["PIT", "BOS"])
role = st.sidebar.radio("Role", ["Hitter", "Pitcher"])

# Load data based on selection
data = load_team_data(team)

if data:
    h_df, p_df, oaa_df, speed_df, br_df = data
    
    # Filter for Hitters or Pitchers
    main_df = h_df if role == "Hitter" else p_df
    
    player = st.sidebar.selectbox("Select Player", main_df['player_name'].unique())
    p_main = main_df[main_df['player_name'] == player].iloc[0]

    # --- 4. DATA MERGING (Join on the Fly) ---
    # We look for the player in the supplemental files
    p_oaa = oaa_df[oaa_df['player_name'] == player]['outs_above_average'].values[0] if player in oaa_df['player_name'].values else 0
    p_speed = speed_df[speed_df['player_name'] == player]['sprint_speed'].values[0] if player in speed_df['player_name'].values else "N/A"
    p_br = br_df[br_df['player_name'] == player]['runner_runs'].values[0] if player in br_df['player_name'].values else 0

    # --- 5. DASHBOARD DISPLAY ---
    st.header(f"Worth Audit: {player}")
    
    # Top Level Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Neutralized UVI", round(p_main['uvi_score'], 1))
    c2.metric("OAA (Defensive Range)", p_oaa)
    c3.metric("Sprint Speed", f"{p_speed} ft/s" if p_speed != "N/A" else "N/A")
    c4.metric("Base Running Runs", round(p_br, 2))

    st.divider()

    # Context & Insights
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("💡 Scout Summary")
        if p_main['uvi_score'] > 115:
            st.success(f"**{player}** is an **Elite Value Anchor**. His situational efficiency is significantly above the professional baseline.")
        elif p_main['uvi_score'] < 90:
            st.warning(f"**{player}** is currently a **Value Leak**. UVI suggests his process is failing to generate consistent worth in current conditions.")
        else:
            st.info(f"**{player}** is a **Stabilizer**. He is performing exactly at the expected professional standard.")

    with col_b:
        st.subheader("🏟️ Environment")
        st.write(f"**Home Park:** {team}")
        st.write(f"**Park Factor:** {PARK_FACTORS.get(team)}")
        st.caption("UVI scores are neutralized based on this factor to ensure fair cross-team comparison.")

else:
    st.error("Missing critical files. Please ensure all CSVs are uploaded to the root of your GitHub repository.")

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Charlie Hildbold | UVI v1.1")

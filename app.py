import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS ---
st.set_page_config(page_title="UVI Worth Engine", layout="wide")
st.markdown("""<style>.stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; }</style>""", unsafe_allow_html=True)

PARK_FACTORS = {'COL': 131, 'MIA': 113, 'BOS': 109, 'PIT': 105, 'SEA': 84}

# --- 2. DATA ENGINE ---
@st.cache_data
def load_team_data(team_code):
    try:
        if team_code == "PIT":
            h = pd.read_csv('pirates_hitting_summary.csv')
            p = pd.read_csv('pirates_pitching_summary.csv')
            oaa = pd.read_csv('outs_above_average.csv')
            speed = pd.read_csv('sprint_speed.csv')
        else: # BOS
            h = pd.read_csv('redsox_hitting_summary.csv')
            p = pd.read_csv('redsox_pitching_summary.csv')
            oaa = pd.read_csv('outs_above_average (1).csv')
            speed = pd.read_csv('sprint_speed (1).csv')

        def match_names(df):
            if df.empty: return df
            if 'last_name, first_name' in df.columns:
                df['player_name'] = df['last_name, first_name'].str.split(', ').str[1] + " " + df['last_name, first_name'].str.split(', ').str[0]
            return df

        return h, p, match_names(oaa), match_names(speed)
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None

# --- 3. UI ---
st.title("⚾ Unified Value Index (UVI)")
team = st.sidebar.selectbox("Select Team", ["PIT", "BOS"])
role = st.sidebar.radio("Role", ["Hitter", "Pitcher"])

data = load_team_data(team)

if data:
    h_df, p_df, oaa_df, speed_df = data
    main_df = h_df if role == "Hitter" else p_df
    
    player = st.sidebar.selectbox("Select Player", main_df['player_name'].unique())
    p_main = main_df[main_df['player_name'] == player].iloc[0]

    # Join Metrics
    p_oaa = oaa_df[oaa_df['player_name'] == player]['outs_above_average'].values[0] if player in oaa_df['player_name'].values else 0
    p_speed = speed_df[speed_df['player_name'] == player]['sprint_speed'].values[0] if player in speed_df['player_name'].values else "N/A"

    # --- 4. DISPLAY ---
    st.header(f"Worth Audit: {player}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Neutralized UVI", round(p_main['uvi_score'], 1))
    c2.metric("Defensive Range (OAA)", p_oaa)
    c3.metric("Sprint Speed", f"{p_speed} ft/s" if p_speed != "N/A" else "N/A")

    st.divider()
    
    # Scout AI Summary
    uvi = p_main['uvi_score']
    if uvi > 120:
        st.success(f"**Elite Performance:** {player} is operating significantly above the major league baseline.")
    elif uvi > 105:
        st.info(f"**Reliable Anchor:** {player} provides stable, above-average value to the roster.")
    else:
        st.warning(f"**Value Under Review:** {player} is currently performing at or below the replacement baseline.")

    # Leaderboard
    st.subheader(f"Top 5 {role}s: {team}")
    st.table(main_df.sort_values('uvi_score', ascending=False).head(5)[['player_name', 'uvi_score']])

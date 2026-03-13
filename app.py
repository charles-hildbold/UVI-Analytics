import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64

# --- 1. CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="UVI Analytics",
    page_icon="icon.png", 
    layout="wide"
)

# --- 2. BACKGROUND & STYLING ENGINE ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def apply_custom_styles(bg_file):
    bin_str = get_base64(bg_file)
    
    # Fallback to dark grey if the image isn't found
    bg_style = f'url("data:image/png;base64,{bin_str}")' if bin_str else "linear-gradient(#0e1117, #0e1117)"
    
    style_code = f'''
    <style>
    /* Main App Background */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), {bg_style};
        background-size: cover;
        background-attachment: fixed;
    }}

    /* Frosted glass effect for metric cards */
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
    }}

    /* FIXING TEXT COLORS */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: #FFFFFF !important; 
    }}
    
    /* Gold for UVI Numbers */
    div[data-testid="stMetricValue"] {{
        color: #FFD700 !important;
        font-weight: bold;
    }}

    /* --- SIDEBAR VISIBILITY FIX --- */
    section[data-testid="stSidebar"] {{
        background-color: #111111 !important; /* Deep black sidebar */
    }}
    
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2 {{
        color: white !important;
    }}

    /* Fix for selectbox/radio text in sidebar */
    div[data-testid="stWidgetLabel"] p {{
        color: white !important;
    }}
    </style>
    '''
    st.markdown(style_code, unsafe_allow_html=True)

# Apply styles using your renamed stadium image
apply_custom_styles('stadium_bg.jpg')

# --- 3. TOP BRANDING ---
try:
    st.image("header.png", use_container_width=True)
except:
    st.title("Unified Value Index (UVI)")

# --- 4. DATA LOGIC & PARK FACTORS ---
PARK_FACTORS = {'COL': 131, 'MIA': 113, 'BOS': 109, 'PIT': 105, 'SEA': 84, 'NYY': 98}

# --- 2. DATA LOADING ---
@st.cache_data
def load_game_data(team):
    try:
        if team == "PIT":
            h = pd.read_csv('pit_h_games.csv')
            p = pd.read_csv('pit_p_games.csv')
        else:
            h = pd.read_csv('bos_h_games.csv')
            p = pd.read_csv('bos_p_games.csv')
        
        for df in [h, p]:
            df['game_date'] = pd.to_datetime(df['game_date'])
            df['month'] = df['game_date'].dt.strftime('%B')
        return h, p
    except:
        return pd.DataFrame(), pd.DataFrame()

# --- 3. UI SIDEBAR ---
st.sidebar.title("⚾ UVI Master Control")
mode = st.sidebar.radio("Analysis Mode", ["Historical Audit", "Predictive Simulator"])
team = st.sidebar.selectbox("Select Team", ["PIT", "BOS"])
role = st.sidebar.radio("Role", ["Hitter", "Pitcher"])

h_df, p_df = load_game_data(team)
active_df = h_df if role == "Hitter" else p_df

if not active_df.empty:
    player = st.sidebar.selectbox("Search Player", active_df['player_name'].unique())
    p_data = active_df[active_df['player_name'] == player]

    # --- 4. HISTORICAL AUDIT MODE ---
    if mode == "Historical Audit":
        st.title(f"📊 Historical Audit: {player}")
        granularity = st.radio("View Level", ["Full Season", "Monthly", "Single Game"], horizontal=True)

        if granularity == "Full Season":
            display_df = p_data.groupby('player_name').agg({'shift':'sum', 'pitch_count':'sum', 'global_mean_spp':'first'}).reset_index()
        elif granularity == "Monthly":
            display_df = p_data.groupby(['player_name', 'month']).agg({'shift':'sum', 'pitch_count':'sum', 'global_mean_spp':'first'}).reset_index()
            selected_month = st.selectbox("Select Month", display_df['month'].unique())
            display_df = display_df[display_df['month'] == selected_month]
        else: # Single Game
            selected_date = st.selectbox("Select Game Date", p_data['game_date'].dt.date.unique())
            display_df = p_data[p_data['game_date'].dt.date == selected_date]

        # Calculate UVI
        row = display_df.iloc[0]
        spp = row['shift'] / row['pitch_count']
        uvi = 100 + ((spp - row['global_mean_spp']) * 150)

        # Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric("Historical UVI", round(uvi, 1))
        c2.metric("Pitch/Plate Samples", int(row['pitch_count']))
        c3.metric("Baseline Mean", round(row['global_mean_spp'], 3))

        st.divider()
        st.subheader("Performance Trend")
        trend = p_data.sort_values('game_date')
        trend['rolling_uvi'] = 100 + (((trend['shift']/trend['pitch_count']) - trend['global_mean_spp']) * 150)
        fig = px.line(trend, x='game_date', y='rolling_uvi', markers=True, title="Game-by-Game UVI Stability")
        st.plotly_chart(fig, use_container_width=True)

    # --- 5. PREDICTIVE SIMULATOR MODE ---
    else:
        st.title(f"🔮 Predictive Simulator: {player}")
        st.info("Simulating performance based on 2025 Career-to-Date averages.")
        
        # Get Career Mean
        career_agg = p_data.groupby('player_name').agg({'shift':'sum', 'pitch_count':'sum', 'global_mean_spp':'first'}).iloc[0]
        career_spp = career_agg['shift'] / career_agg['pitch_count']
        
        target_park = st.selectbox("Simulate in Stadium:", list(PARK_FACTORS.keys()))
        temp = st.slider("Forecasted Temperature (°F)", 30, 110, 72)

        # Sim Logic
        home_pf = PARK_FACTORS.get(team, 100)
        target_pf = PARK_FACTORS.get(target_park, 100)
        
        # Neutralize and re-apply
        neutral_spp = career_spp / (home_pf / 100)
        pred_spp = neutral_spp * (target_pf / 100)
        weather_adj = (temp - 72) * 0.002
        final_pred_spp = pred_spp + weather_adj
        
        pred_uvi = 100 + ((final_pred_spp - career_agg['global_mean_spp']) * 150)

        st.metric("Predicted UVI Worth", round(pred_uvi, 1), 
                  delta=f"{round(pred_uvi - (100+((career_spp-career_agg['global_mean_spp'])*150)), 1)} Env Shift")
        
        st.success(f"**Scout Note:** If moved to **{target_park}**, {player}'s neutralized worth shifts due to park dimensions and atmospheric density.")

else:
    st.error("No game-level data found. Please upload the granular CSV files.")

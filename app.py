import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- 1. APP CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

if 'app_theme' not in st.session_state: 
    st.session_state.app_theme = "Dark" # Defaults to Dark on first open
if 'display_count' not in st.session_state: 
    st.session_state.display_count = 20

# --- 2. THEME ENGINE (ROOT VARIABLE OVERRIDES) ---
if st.session_state.app_theme == "Dark":
    m_bg, m_txt, m_card, m_input = "#0e1117", "#FFFFFF", "rgba(255,255,255,0.05)", "rgba(255,255,255,0.05)"
    m_border, m_sub = "rgba(255,255,255,0.1)", "rgba(255,255,255,0.6)"
elif st.session_state.app_theme == "Light":
    m_bg, m_txt, m_card, m_input = "#FFFFFF", "#000000", "rgba(0,0,0,0.05)", "#f0f2f6"
    m_border, m_sub = "rgba(0,0,0,0.1)", "rgba(0,0,0,0.6)"
else: # System Default
    m_bg, m_txt, m_card, m_input = "transparent", "inherit", "rgba(128,128,128,0.05)", "rgba(128,128,128,0.05)"
    m_border, m_sub = "rgba(128,128,128,0.1)", "gray"

# --- 3. TOP NAVIGATION (Settings Top-Right) ---
t_col1, t_col2 = st.columns([5, 1.2])

with t_col1:
    st.title("🎵 Music Recommendation System")

with t_col2:
    with st.popover("⚙️ Settings", use_container_width=True):
        st.markdown(f"### Appearance")
        theme_choice = st.selectbox(
            "Select Theme", ["Dark", "Light", "System Default"], 
            index=0 if st.session_state.app_theme == "Dark" else 1
        )
        if theme_choice != st.session_state.app_theme:
            st.session_state.app_theme = theme_choice
            st.rerun()

# --- 4. THE ULTIMATE CSS (Targets Streamlit Internal Variables) ---
st.markdown(f"""
    <style>
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display:none !important;}}

    /* FORCE ROOT VARIABLES - This fixes the search and settings colors */
    :root {{
        --text-color: {m_txt};
        --background-color: {m_bg};
        --primary-color: #1DB954;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {m_bg} !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
        color: {m_txt} !important;
    }}

    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* SEARCH BAR & INPUTS */
    .stTextInput input {{ 
        background-color: {m_input} !important;
        color: {m_txt} !important;
        border: 1px solid {m_border} !important;
        border-radius: 15px !important;
    }}

    /* PLAY BUTTONS (Link Buttons) */
    [data-testid="stLinkButton"] > a {{
        background-color: #1DB954 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        transition: 0.3s !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
    }}
    [data-testid="stLinkButton"] > a:hover {{
        background-color: #1ed760 !important;
        transform: scale(1.02);
    }}

    /* SETTINGS POPOVER CONTENT */
    div[data-testid="stPopoverContent"] {{
        background-color: {m_bg} !important;
        border: 1px solid {m_border} !important;
        color: {m_txt} !important;
    }}

    /* MOOD SELECTOR COLORS */
    div[role="radiogroup"] {{ display: flex; flex-wrap: wrap !important; gap: 8px; margin-top: 10px; }}
    div[role="radiogroup"] label {{
        padding: 0px 15px; min-width: 110px; height: 48px; 
        display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; color: white !important; cursor: pointer; 
    }}

    /* MOOD GRADIENTS */
    div[role="radiogroup"] label:nth-of-type(1) {{ background: linear-gradient(135deg, #667eea, #764ba2); }} 
    div[role="radiogroup"] label:nth-of-type(2) {{ background: linear-gradient(135deg, #2b5876, #4e4376); }} 
    div[role="radiogroup"] label:nth-of-type(3) {{ background: linear-gradient(135deg, #ff4e50, #f9d423); }} 
    div[role="radiogroup"] label:nth-of-type(4) {{ background: linear-gradient(135deg, #0ba360, #3cba92); }} 
    div[role="radiogroup"] label:nth-of-type(5) {{ background: linear-gradient(135deg, #FF512F, #DD2476); }} 
    div[role="radiogroup"] label:nth-of-type(6) {{ background: linear-gradient(135deg, #4b6cb7, #182848); }} 
    div[role="radiogroup"] label:nth-of-type(7) {{ background: linear-gradient(135deg, #00d2ff, #3a7bd5); }} 
    div[role="radiogroup"] label:nth-of-type(8) {{ background: linear-gradient(135deg, #f80759, #bc4e9c); }} 

    div[role="radiogroup"] [data-checked="true"] + div {{ 
        transform: scale(1.05); border: 2.5px solid white !important;
    }}

    /* SONG CARDS */
    .song-card {{
        padding: 25px; border-radius: 20px;
        background: {m_card}; backdrop-filter: blur(15px);
        border: 1px solid {m_border}; margin-bottom: 12px;
    }}
    .song-card:hover {{ border-color: #1DB954; }}

    .footer-container {{
        margin-top: 80px; padding: 50px; text-align: center;
        border-top: 1px solid {m_border};
    }}
    .footer-names {{
        font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #667eea, #ff0844);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

st.markdown(f"<p style='color: {m_sub} !important; font-size: 1.1rem; font-weight: 300; margin-top: -15px;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # Search Box
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        st.write("### ✨ Match your Mood")
        mood_choices = ["All Songs", "Sad", "Romantic", "Workout", "Party", "Focus", "Chill", "Dance"]
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # Logic
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.4)]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6) & (f_df['Energy'] < 0.6)]
        elif mood_choice == "Workout": f_df = f_df[(f_df['Energy'] > 0.7) & (f_df['Tempo'] > 115)]
        elif mood_choice == "Party": f_df = f_df[(f_df['Danceability'] > 0.7) & (f_df['Energy'] > 0.7)]
        elif mood_choice == "Focus": f_df = f_df[(f_df['Instrumentalness'] > 0.4) | (f_df['Energy'] < 0.5)]
        elif mood_choice == "Chill": f_df = f_df[(f_df['Energy'] < 0.4) & (f_df['Loudness'] < -10)]
        elif mood_choice == "Dance": f_df = f_df[(f_df['Danceability'] > 0.8)]

        # Counter
        st.metric(label="Songs Found", value=len(f_df))
        st.write("---")

        if f_df.empty:
            st.warning("No songs found.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="color: {m_sub} !important; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                        <div style="margin-top: 15px;">
                            <span style="background: rgba(29, 185, 84, 0.2); color: #1DB954; padding: 5px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                u = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)
                st.write("")

            if show_now < len(recs):
                if st.button("⬇️ Show More Songs", use_container_width=True):
                    st.session_state.display_count += 20
                    st.rerun()

        # --- TEAM FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: {m_sub} !important; font-size: 0.8rem; letter-spacing: 4px; margin-bottom: 12px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: {m_sub} !important; font-size: 0.75rem; margin-top: 25px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

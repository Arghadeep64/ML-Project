import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- MOBILE-OPTIMIZED UI CONFIG ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

# 1. STATE INITIALIZATION
if 'app_theme' not in st.session_state: st.session_state.app_theme = "Dark"
if 'display_count' not in st.session_state: st.session_state.display_count = 20

# --- TOP NAVIGATION (Mobile Optimized Top-Right Settings) ---
# We use a 4:1 ratio to ensure the button stays on the right even on small screens
t_col1, t_col2 = st.columns([4, 1])

with t_col1:
    st.title("🎵 Music Recommendation System")

with t_col2:
    # Popover acts as a sleek modern menu
    with st.popover("⚙️ Settings", use_container_width=True):
        st.markdown("### 🛠️ App Appearance")
        theme_choice = st.selectbox(
            "Appearance", ["Dark", "Light", "System Default"], 
            index=0 if st.session_state.app_theme == "Dark" else 1
        )
        st.session_state.app_theme = theme_choice

st.markdown("<p style='opacity: 0.8; font-size: 1.1rem; font-weight: 300; margin-top: -15px;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

# 2. DYNAMIC THEME ENGINE
if st.session_state.app_theme == "Dark":
    bg_color, text_color, input_bg = "rgba(10, 10, 10, 1)", "#FFFFFF", "rgba(255, 255, 255, 0.05)"
    glass_border = "rgba(255, 255, 255, 0.1)"
elif st.session_state.app_theme == "Light":
    bg_color, text_color, input_bg = "#f8f9fa", "#000000", "rgba(255, 255, 255, 0.9)"
    glass_border = "rgba(0, 0, 0, 0.1)"
else: # System
    bg_color, text_color, input_bg = "transparent", "inherit", "rgba(128, 128, 128, 0.05)"
    glass_border = "rgba(128, 128, 128, 0.1)"

# 3. FLAWLESS CSS (Background Motion Enabled by Default)
st.markdown(f"""
    <style>
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display:none !important;}}

    /* MODERN SMOOTH BACKGROUND WITH PERMANENT MOTION */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(29, 185, 84, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.12) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
        color: {text_color};
    }}

    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* MOBILE OPTIMIZED INPUTS */
    .stTextInput input {{ 
        border-radius: 15px; 
        border: 1px solid rgba(128,128,128,0.2); 
        padding: 12px; 
        background: {input_bg} !important;
        backdrop-filter: blur(10px);
        color: {text_color} !important;
        font-size: 16px !important; /* Prevents auto-zoom on iOS */
    }}
    
    div[role="radiogroup"] {{ 
        display: flex; 
        flex-wrap: wrap !important; 
        justify-content: flex-start; 
        gap: 8px; 
        margin-top: 10px; 
    }}
    
    div[role="radiogroup"] label {{
        flex: 1; min-width: 100px; height: 45px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; color: white !important; cursor: pointer; 
        transition: 0.3s ease; font-size: 0.85rem !important;
    }}
    
    /* GORGEOUS MOOD GRADIENTS */
    div[role="radiogroup"] label:nth-of-type(1) {{ background: linear-gradient(135deg, #667eea, #764ba2); }} 
    div[role="radiogroup"] label:nth-of-type(2) {{ background: linear-gradient(135deg, #2b5876, #4e4376); }} 
    div[role="radiogroup"] label:nth-of-type(3) {{ background: linear-gradient(135deg, #ff0844, #ffb199); }} 
    div[role="radiogroup"] label:nth-of-type(4) {{ background: linear-gradient(135deg, #0ba360, #3cba92); }} 
    div[role="radiogroup"] label:nth-of-type(5) {{ background: linear-gradient(135deg, #FF512F, #DD2476); }} 
    div[role="radiogroup"] label:nth-of-type(6) {{ background: linear-gradient(135deg, #4b6cb7, #182848); }} 
    div[role="radiogroup"] label:nth-of-type(7) {{ background: linear-gradient(135deg, #00d2ff, #3a7bd5); }} 
    div[role="radiogroup"] label:nth-of-type(8) {{ background: linear-gradient(135deg, #f80759, #bc4e9c); }} 
    
    div[role="radiogroup"] label:nth-of-type(1)::after {{ content: "Everything"; }}
    div[role="radiogroup"] label:nth-of-type(2)::after {{ content: "Sad"; }}
    div[role="radiogroup"] label:nth-of-type(3)::after {{ content: "Romantic"; }}
    div[role="radiogroup"] label:nth-of-type(4)::after {{ content: "Workout"; }}
    div[role="radiogroup"] label:nth-of-type(5)::after {{ content: "Party"; }}
    div[role="radiogroup"] label:nth-of-type(6)::after {{ content: "Focus"; }}
    div[role="radiogroup"] label:nth-of-type(7)::after {{ content: "Chill"; }}
    div[role="radiogroup"] label:nth-of-type(8)::after {{ content: "Dance"; }}

    div[role="radiogroup"] [data-checked="true"] + div {{ transform: scale(1.05); border: 2px solid white !important; box-shadow: 0 0 15px rgba(255,255,255,0.2); }}

    /* FLAWLESS GLASS CARDS */
    .song-card {{
        padding: 20px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.1); 
        backdrop-filter: blur(15px);
        border: 1px solid {glass_border}; 
        margin-bottom: 10px;
        transition: 0.3s ease;
    }}
    .song-card:hover {{ border-color: #1DB954; }}

    .footer-container {{
        margin-top: 80px; padding: 40px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }}
    .footer-names {{
        font-weight: 300; letter-spacing: 4px; text-transform: uppercase; font-size: 1.1rem;
        background: linear-gradient(to right, #667eea, #ff0844);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # Search Box
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        # Mood Selection
        mood_choices = ["All", "Sad", "Romantic", "Gym", "Party", "Study", "Chill", "Dance"]
        st.write("### ✨ Match your Mood")
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC ---
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.4)]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6) & (f_df['Energy'] < 0.6)]
        elif mood_choice == "Gym": f_df = f_df[(f_df['Energy'] > 0.7) & (f_df['Tempo'] > 115)]
        elif mood_choice == "Party": f_df = f_df[(f_df['Danceability'] > 0.7) & (f_df['Energy'] > 0.7)]
        elif mood_choice == "Study": f_df = f_df[(f_df['Instrumentalness'] > 0.4) | (f_df['Energy'] < 0.5)]
        elif mood_choice == "Chill": f_df = f_df[(f_df['Energy'] < 0.4) & (f_df['Loudness'] < -10)]
        elif mood_choice == "Dance": f_df = f_df[(f_df['Danceability'] > 0.8)]

        # --- TRACKS FOUND COUNTER ---
        st.metric(label="Songs Found", value=len(f_df))
        st.write("---")

        if f_df.empty:
            st.warning("No songs found for this selection.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.3rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.7; font-size: 1rem; margin-top: 5px;">{row['ArtistName']}</div>
                        <div style="margin-top: 12px;">
                            <span style="background: rgba(29, 185, 84, 0.2); padding: 4px 10px; border-radius: 10px; font-size: 0.75rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
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
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 10px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 20px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

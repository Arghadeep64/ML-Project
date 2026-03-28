import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- 1. THEME & STATE INITIALIZATION ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

# Default to Dark on first run
if 'app_theme' not in st.session_state: 
    st.session_state.app_theme = "Dark"
if 'display_count' not in st.session_state: 
    st.session_state.display_count = 20

# --- 2. TOP NAVIGATION (Mobile Optimized Top-Right Settings) ---
t_col1, t_col2 = st.columns([5, 1.2])

with t_col1:
    st.title("🎵 Music Recommendation System")

with t_col2:
    # Placed in top right
    with st.popover("⚙️ Settings", use_container_width=True):
        st.markdown("### Appearance")
        theme_choice = st.selectbox(
            "Select Theme", ["Dark", "Light", "System Default"], 
            index=0 if st.session_state.app_theme == "Dark" else 1
        )
        if theme_choice != st.session_state.app_theme:
            st.session_state.app_theme = theme_choice
            st.rerun()

# --- 3. DYNAMIC THEME COLOR ENGINE ---
if st.session_state.app_theme == "Dark":
    main_bg = "#0e1117"
    text_main = "#FFFFFF"
    card_bg = "rgba(255, 255, 255, 0.05)"
    border_color = "rgba(255, 255, 255, 0.1)"
    sub_text = "rgba(255, 255, 255, 0.6)"
    metric_color = "#1DB954"
elif st.session_state.app_theme == "Light":
    main_bg = "#FFFFFF"
    text_main = "#121212"
    card_bg = "rgba(0, 0, 0, 0.03)"
    border_color = "rgba(0, 0, 0, 0.1)"
    sub_text = "rgba(0, 0, 0, 0.6)"
    metric_color = "#1aa34a"
else: # System Default
    main_bg = "transparent"
    text_main = "inherit"
    card_bg = "rgba(128, 128, 128, 0.05)"
    border_color = "rgba(128, 128, 128, 0.1)"
    sub_text = "gray"
    metric_color = "#1DB954"

# --- 4. THE MASTER CSS (Flawless Design) ---
st.markdown(f"""
    <style>
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display:none !important;}}

    /* ADAPTIVE BACKGROUND & TEXT */
    [data-testid="stAppViewContainer"] {{
        background-color: {main_bg};
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
        color: {text_main} !important;
    }}

    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* FORCE ALL HEADERS TO BE VISIBLE */
    h1, h2, h3, p, span, label, .stMetric div {{
        color: {text_main} !important;
    }}

    /* SEARCH INPUT FIX */
    .stTextInput input {{ 
        border-radius: 15px; border: 1px solid {border_color}; 
        padding: 12px; background: {card_bg} !important;
        color: {text_main} !important; font-size: 16px !important;
    }}

    /* MOOD SELECTOR (Fixing the double-label and wrap bug) */
    div[role="radiogroup"] {{ 
        display: flex; flex-wrap: wrap !important; gap: 8px; margin-top: 10px; 
    }}
    
    div[role="radiogroup"] label {{
        padding: 0px 15px;
        min-width: 110px; height: 48px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; color: white !important; cursor: pointer; 
        transition: 0.3s ease;
    }}

    /* Hide the default radio circle */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.85rem !important; margin: 0; padding: 0;
    }}
    
    /* GORGEOUS MOOD GRADIENTS */
    div[role="radiogroup"] label:nth-of-type(1) {{ background: linear-gradient(135deg, #667eea, #764ba2); }} 
    div[role="radiogroup"] label:nth-of-type(2) {{ background: linear-gradient(135deg, #2b5876, #4e4376); }} 
    div[role="radiogroup"] label:nth-of-type(3) {{ background: linear-gradient(135deg, #ff4e50, #f9d423); }} /* Proper Romantic */
    div[role="radiogroup"] label:nth-of-type(4) {{ background: linear-gradient(135deg, #0ba360, #3cba92); }} 
    div[role="radiogroup"] label:nth-of-type(5) {{ background: linear-gradient(135deg, #FF512F, #DD2476); }} 
    div[role="radiogroup"] label:nth-of-type(6) {{ background: linear-gradient(135deg, #4b6cb7, #182848); }} 
    div[role="radiogroup"] label:nth-of-type(7) {{ background: linear-gradient(135deg, #00d2ff, #3a7bd5); }} 
    div[role="radiogroup"] label:nth-of-type(8) {{ background: linear-gradient(135deg, #f80759, #bc4e9c); }} 

    div[role="radiogroup"] [data-checked="true"] + div {{ 
        transform: scale(1.05); border: 2.5px solid white !important; box-shadow: 0 0 15px rgba(255,255,255,0.3); 
    }}

    /* FLAWLESS SONG CARDS */
    .song-card {{
        padding: 25px; border-radius: 20px;
        background: {card_bg}; backdrop-filter: blur(15px);
        border: 1px solid {border_color}; margin-bottom: 12px;
        transition: 0.3s ease;
    }}
    .song-card:hover {{ border-color: #1DB954; transform: translateY(-3px); }}

    .footer-container {{
        margin-top: 80px; padding: 50px; text-align: center;
        border-top: 1px solid {border_color};
    }}
    .footer-names {{
        font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #667eea, #ff0844);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOGIC ---
@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

st.markdown(f"<p style='color: {sub_text}; font-size: 1.1rem; font-weight: 300; margin-top: -15px;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # Search Box
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        st.write("### ✨ Match your Mood")
        # Fix: Using the exact words as the options to stop the repeating bug
        mood_choices = ["Everything", "Sad", "Romantic", "Workout", "Party", "Focus", "Chill", "Dance"]
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
            st.warning("No songs found for this selection.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="color: {sub_text}; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
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
                <p style="color: {sub_text}; font-size: 0.8rem; letter-spacing: 4px; margin-bottom: 12px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: {sub_text}; font-size: 0.75rem; margin-top: 25px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

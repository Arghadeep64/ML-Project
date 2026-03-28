import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- MASTERPIECE UI CONFIG ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

# 1. SETTINGS & STATE INITIALIZATION
if 'app_theme' not in st.session_state: st.session_state.app_theme = "Dark"
if 'bg_animation' not in st.session_state: st.session_state.bg_animation = True
if 'display_count' not in st.session_state: st.session_state.display_count = 20
if 'card_opacity' not in st.session_state: st.session_state.card_opacity = 0.08

# --- TOP NAVIGATION BAR (Settings Button on Top Right) ---
t_col1, t_col2 = st.columns([5, 1])

with t_col2:
    with st.popover("⚙️ Settings", use_container_width=True):
        st.markdown("### 🛠️ App Controls")
        
        # Theme Toggle
        theme_choice = st.selectbox(
            "Appearance", ["Dark", "Light", "System Default"], 
            index=0 if st.session_state.app_theme == "Dark" else 1
        )
        st.session_state.app_theme = theme_choice
        
        # Animation Toggle
        st.session_state.bg_animation = st.toggle("Enable Background Motion", value=True)
        
        # Results per load
        st.session_state.display_count = st.select_slider(
            "Songs per load", options=[10, 20, 50, 100], value=20
        )
        
        # Card Transparency
        st.session_state.card_opacity = st.slider("Glass Transparency", 0.01, 0.20, 0.08)

# 2. DYNAMIC THEME ENGINE
if st.session_state.app_theme == "Dark":
    bg_color, text_color, input_bg = "rgba(10, 10, 10, 1)", "#FFFFFF", "rgba(255, 255, 255, 0.05)"
    glass_border = "rgba(255, 255, 255, 0.1)"
elif st.session_state.app_theme == "Light":
    bg_color, text_color, input_bg = "#f0f2f6", "#000000", "rgba(255, 255, 255, 0.8)"
    glass_border = "rgba(0, 0, 0, 0.1)"
else: # System
    bg_color, text_color, input_bg = "transparent", "inherit", "rgba(128, 128, 128, 0.05)"
    glass_border = "rgba(128, 128, 128, 0.1)"

# 3. ADVANCED CSS
anim_css = "animation: gradientMove 15s ease infinite;" if st.session_state.bg_animation else ""

st.markdown(f"""
    <style>
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display:none !important;}}

    /* MODERN SMOOTH BACKGROUND */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(29, 185, 84, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.12) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px);
        background-size: 400% 400%;
        {anim_css}
        background-attachment: fixed;
        color: {text_color};
    }}

    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .stTextInput input {{ 
        border-radius: 20px; 
        border: 1px solid rgba(128,128,128,0.2); 
        padding: 15px; 
        background: {input_bg} !important;
        backdrop-filter: blur(10px);
        color: {text_color} !important;
    }}
    
    div[role="radiogroup"] {{ display: flex; flex-wrap: wrap !important; justify-content: center; gap: 10px; margin-top: 15px; }}
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] {{ display: none; }}
    div[role="radiogroup"] [data-testid="stWidgetLabel"] {{ display: none; }}
    div[role="radiogroup"] label p {{ display: none; }}
    
    div[role="radiogroup"] label {{
        flex: 1; min-width: 120px; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.4s;
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

    div[role="radiogroup"] [data-checked="true"] + div {{ transform: scale(1.1); border: 3px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.2); }}

    .song-card {{
        padding: 30px; border-radius: 25px;
        background: rgba(128, 128, 128, {st.session_state.card_opacity}); 
        backdrop-filter: blur(20px);
        border: 1px solid {glass_border}; 
        margin-bottom: 10px;
        transition: 0.4s ease;
    }}
    .song-card:hover {{ transform: translateY(-5px); border-color: #1DB954; }}

    .footer-container {{
        margin-top: 100px; padding: 60px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }}
    .footer-names {{
        font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.3rem;
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

# --- APP LAYOUT ---
with t_col1:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.8; font-size: 1.2rem; font-weight: 300;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # Search Box
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        # Mood Selection
        mood_choices = ["All", "Sad", "Romantic", "Gym", "Party", "Study", "Chill", "Dance"]
        st.write("### ✨ Match your Mood")
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC (UNTOUCHED) ---
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
                        <div style="font-weight: 900; font-size: 1.5rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.6; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                        <div style="margin-top: 15px;">
                            <span style="background: rgba(29, 185, 84, 0.2); padding: 5px 15px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
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
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 15px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 25px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- PROFESSIONAL & ADAPTIVE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}

    /* 2. ARTISTIC BACKGROUND (Works in Light & Dark Mode) */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(29, 185, 84, 0.1) 0%, transparent 35%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.1) 0%, transparent 35%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px); /* Subtle Grid Dots */
        background-size: 100% 100%, 100% 100%, 30px 30px;
        background-attachment: fixed;
    }

    /* 3. NEON MOOD BUTTONS */
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; gap: 10px; margin-top: 15px; }
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.3s;
    }
    div[role="radiogroup"] label:nth-of-type(1) { background: #1DB954; } /* Spotify Green */
    div[role="radiogroup"] label:nth-of-type(2) { background: #1e3c72; } /* Deep Blue */
    div[role="radiogroup"] label:nth-of-type(3) { background: #f953c6; } /* Pink */
    div[role="radiogroup"] label:nth-of-type(4) { background: #f7971e; } /* Orange */
    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.05); border: 2.5px solid white !important; }

    /* 4. GLASSMORPHISM SONG CARDS */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 10px;
        transition: 0.3s;
    }
    .song-card:hover { border-color: #1DB954; transform: translateX(10px); }

    /* 5. TEAM FOOTER (No <br> used) */
    .footer-container {
        margin-top: 100px; padding: 40px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #1DB954, #00B4DB);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# State management for "Load More"
if 'display_limit' not in st.session_state: st.session_state.display_limit = 10

# --- HEADER ---
st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.6;'>A Data-Driven Mood Discovery Experience</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if not df.empty:
        # Search & Filters
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        mood_choice = st.radio("Vibe:", ["All Songs", "Sad", "Romantic", "Happy"], horizontal=True, label_visibility="collapsed")

        # --- ML FILTERING LOGIC ---
        f_df = df.copy()
        if search_query:
            f_df = f_df[f_df['SongName'].str.contains(search_query, case=False, na=False) | 
                        f_df['ArtistName'].str.contains(search_query, case=False, na=False)]
        
        if mood_choice == "Sad": f_df = f_df[f_df['Valence'] < 0.4]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6)]
        elif mood_choice == "Happy": f_df = f_df[f_df['Valence'] > 0.6]

        st.write(f"Discovery: **{len(f_df.head(st.session_state.display_limit))}** tracks found.")

        # --- DISPLAY RESULTS ---
        for i, row in f_df.head(st.session_state.display_limit).iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="song-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: #1DB954;">{row['SongName']}</h3>
                                <p style="opacity: 0.7; margin: 0;">{row['ArtistName']}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 0.7rem; opacity: 0.5; text-transform: uppercase;">Acousticness</span><br>
                                <b style="font-size: 1.1rem; color: #1DB954;">{int(row['Acousticness']*100)}%</b>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # STABLE SPOTIFY LINK
                spotify_url = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"▶️ Open {row['SongName']} in Spotify", spotify_url, use_container_width=True)
                st.write("")

        if st.session_state.display_limit < len(f_df):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_limit += 10
                st.rerun()

        # --- TEAM FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <div class="footer-names">Buddhadeb • Arghadeep • Sanajit • Kamalakanta</div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 20px; letter-spacing: 2px;">CSE PROJECT • 2026</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading system: {e}")

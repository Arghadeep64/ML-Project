import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- PROFESSIONAL SPOTIFY-THEMED UI ---
st.set_page_config(page_title="Spotify Recommendation System", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}

    /* ARTISTIC ABSTRACT BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.15) 0%, transparent 40%), /* Spotify Green Glow */
            radial-gradient(circle at 90% 80%, rgba(30, 60, 114, 0.1) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.1) 1.5px, transparent 1.5px);
        background-size: 100% 100%, 100% 100%, 35px 35px;
        background-attachment: fixed;
    }

    /* GLASSMORPHISM SONG CARDS */
    .song-card {
        padding: 30px; border-radius: 25px;
        background: rgba(25, 20, 20, 0.05); /* Spotify Dark Tint */
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1); 
        margin-bottom: 15px;
        transition: 0.4s ease;
    }
    .song-card:hover { transform: translateY(-5px); border-color: #1DB954; box-shadow: 0 10px 30px rgba(29, 185, 84, 0.1); }

    /* SPOTIFY STYLE BUTTON */
    .stButton button {
        background: #1DB954 !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* MOOD SELECTOR */
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; gap: 12px; margin-top: 20px; }
    div[role="radiogroup"] label {
        flex: 1; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer;
    }
    div[role="radiogroup"] label:nth-of-type(1) { background: #1DB954; } /* All - Spotify Green */
    div[role="radiogroup"] label:nth-of-type(2) { background: #1e3c72; } /* Sad */
    div[role="radiogroup"] label:nth-of-type(3) { background: #f953c6; } /* Romantic */
    div[role="radiogroup"] label:nth-of-type(4) { background: #f7971e; } /* Happy */
    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.08); border: 3px solid white !important; }

    /* TEAM FOOTER */
    .footer-container { margin-top: 100px; padding: 50px; text-align: center; border-top: 1px solid rgba(128, 128, 128, 0.1); }
    .footer-names { font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem; background: linear-gradient(to right, #1DB954, #191414); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# --- HEADER ---
st.title("🎵 Spotify Recommendation System")
st.markdown("<h4 style='opacity: 0.6; font-weight: 300;'>Machine Learning based Mood Analysis</h4>", unsafe_allow_html=True)

try:
    df = load_data()
    if not df.empty:
        # User Interaction
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        mood_choice = st.radio("Vibe:", ["All Tracks", "Sad", "Romantic", "Happy"], horizontal=True, label_visibility="collapsed")

        # ML Logic
        f_df = df.copy()
        if search_query:
            f_df = f_df[f_df['SongName'].str.contains(search_query, case=False, na=False) | f_df['ArtistName'].str.contains(search_query, case=False, na=False)]
        
        # Filtering based on Spotify Valence (Mood)
        if mood_choice == "Sad": f_df = f_df[f_df['Valence'] < 0.4]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6)]
        elif mood_choice == "Happy": f_df = f_df[f_df['Valence'] > 0.6]

        st.write(f"Discovery: **{len(f_df.head(10))}** tracks recommended for you")

        # Results Display
        for i, row in f_df.head(10).iterrows():
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
                                <b style="font-size: 1.1rem;">{int(row['Acousticness']*100)}%</b>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # SPOTIFY DEEP LINK (No YouTube Teleporting)
                # This opens the song in the Spotify App or Web Player
                spotify_search_url = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"Listen on Spotify", spotify_search_url, use_container_width=True)
                st.write("")

        # --- FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <div class="footer-names">Buddhadeb • Arghadeep • Sanajit • Kamalakanta</div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 15px; letter-spacing: 2px;">CSE PROJECT • 2026</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading system: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- ADAPTIVE THEME & ARTISTIC UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}

    /* 2. ARTISTIC ABSTRACT BACKGROUND (Works in Light & Dark) */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.12) 0%, transparent 40%),
            /* Floating Small Circles */
            radial-gradient(circle at 50% 50%, rgba(128, 128, 128, 0.05) 2px, transparent 2px);
        background-size: 100% 100%, 100% 100%, 40px 40px;
        background-attachment: fixed;
    }

    /* 3. NEON MOOD SELECTORS */
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; gap: 12px; margin-top: 20px; }
    div[role="radiogroup"] label {
        flex: 1; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 18px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.4s;
    }
    div[role="radiogroup"] label:nth-of-type(1) { background: #1DB954; } 
    div[role="radiogroup"] label:nth-of-type(2) { background: #1e3c72; } 
    div[role="radiogroup"] label:nth-of-type(3) { background: #f953c6; } 
    div[role="radiogroup"] label:nth-of-type(4) { background: #f7971e; }
    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.08); border: 3px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.3); }

    /* 4. GLASSMORPHISM SONG CARDS */
    .song-card {
        padding: 30px; border-radius: 25px;
        background: rgba(128, 128, 128, 0.08); 
        backdrop-filter: blur(20px);
        border: 1px solid rgba(128, 128, 128, 0.1); 
        margin-bottom: 15px;
        transition: 0.4s ease;
    }
    .song-card:hover { border-color: #1DB954; transform: translateY(-5px); }

    /* 5. TEAM FOOTER (Professional Spacing) */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.3rem;
        background: linear-gradient(to right, #1DB954, #444);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# --- HEADER ---
st.title("🎵 Music Recommendation System")
st.markdown("<h4 style='opacity: 0.6; font-weight: 300;'>Explore the rhythm of your mood</h4>", unsafe_allow_html=True)

try:
    df = load_data()
    if not df.empty:
        # Search & Filters
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        mood_choice = st.radio("Vibe:", ["All Tracks", "Sad", "Romantic", "Happy"], horizontal=True, label_visibility="collapsed")

        # ML LOGIC (Mood Filtering)
        f_df = df.copy()
        if search_query:
            f_df = f_df[f_df['SongName'].str.contains(search_query, case=False, na=False) | 
                        f_df['ArtistName'].str.contains(search_query, case=False, na=False)]
        
        if mood_choice == "Sad": f_df = f_df[f_df['Valence'] < 0.4]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.65)]
        elif mood_choice == "Happy": f_df = f_df[f_df['Valence'] > 0.65]

        st.write(f"Discovery: **{len(f_df.head(8))}** tracks recommended")

        # DISPLAY RESULTS
        for i, row in f_df.head(8).iterrows():
            with st.container():
                # Displaying Acousticness as a Data Insight
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
                
                # Spotify Official Link (No YouTube Teleporting)
                search_url = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"Listen to {row['SongName']} on Spotify", search_url, use_container_width=True)
                st.write("")

        # --- FINAL FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <div class="footer-names">Buddhadeb • Arghadeep • Sanajit • Kamalakanta</div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 15px; letter-spacing: 2px;">COMPUTER SCIENCE PROJECT • 2026</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading system: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- ARTISTIC MASTERPIECE CONFIG ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}

    /* DYNAMIC ABSTRACT BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.1) 1.5px, transparent 1.5px);
        background-size: 100% 100%, 100% 100%, 35px 35px;
        background-attachment: fixed;
    }

    /* GLASSMORPHISM SONG CARDS */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px;
        transition: 0.4s ease;
    }
    .song-card:hover { transform: translateY(-5px); border-color: #1DB954; }

    /* NEON MOOD BUTTONS */
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; gap: 15px; margin-top: 15px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    div[role="radiogroup"] label {
        flex: 1; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.3s;
    }
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #00B4DB, #0083B0); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #141E30, #243B55); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #56ab2f, #a8e063); } 
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Tracks"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }
    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.1); border: 3px solid white !important; }

    /* FOOTER */
    .footer-container { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid rgba(128, 128, 128, 0.1); }
    .footer-names { font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem; background: linear-gradient(to right, #00B4DB, #ff4e50); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# --- HEADER ---
st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.6;'>A Data-Driven Exploration of Sound & Mood</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if not df.empty:
        # Search & Filter
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        mood_choice = st.radio("Mood:", ["All Songs", "Sad", "Romantic", "Happy"], horizontal=True, label_visibility="collapsed")

        # Logic
        f_df = df.copy()
        if search_query:
            f_df = f_df[f_df['SongName'].str.contains(search_query, case=False, na=False) | f_df['ArtistName'].str.contains(search_query, case=False, na=False)]
        
        if mood_choice == "Sad": f_df = f_df[f_df['Valence'] < 0.4]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6)]
        elif mood_choice == "Happy": f_df = f_df[f_df['Valence'] > 0.6]

        # Display Results in a Grid
        st.write(f"Showing **{len(f_df.head(10))}** recommendations based on audio features")
        
        for i, row in f_df.head(10).iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="song-card">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <h3 style="margin: 0; color: #1DB954;">{row['SongName']}</h3>
                                <p style="opacity: 0.7;">{row['ArtistName']}</p>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 0.8rem; opacity: 0.5;">Mood Score</span><br>
                                <b style="font-size: 1.2rem;">{int(row['Valence']*100)}%</b>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # The "Action Link" approach is 100% stable
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"▶️ Play {row['SongName']}", search_url, use_container_width=True)
                st.write("")

        # --- FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <div class="footer-names">Buddhadeb • Arghadeep • Sanajit • Kamalakanta</div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 15px;">CSE DEPARTMENT • 2026</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

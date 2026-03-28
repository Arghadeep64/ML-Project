import streamlit as st
import pandas as pd
import numpy as np
import requests
import os

# --- THE ARTISTIC "API-POWERED" UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

# REPLACE THIS WITH YOUR KEY FROM STEP 1
YOUTUBE_API_KEY = "YOUR_API_KEY_HERE" 

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}

    /* ARTISTIC ABSTRACT BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            linear-gradient(rgba(128, 128, 128, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 35px 35px, 35px 35px;
        background-attachment: fixed;
    }

    /* NEON CARDS & BUTTONS */
    .song-card {
        padding: 20px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1DB954, #191414);
        color: white; border: none; border-radius: 12px; font-weight: bold;
    }

    .footer-names {
        margin-top: 50px; text-align: center; font-weight: 200; letter-spacing: 4px;
        background: linear-gradient(to right, #00B4DB, #ff4e50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

def get_video_id(song_name, artist_name):
    try:
        query = f"{song_name} {artist_name} official audio"
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults=1&type=video"
        response = requests.get(url).json()
        return response['items'][0]['id']['videoId']
    except:
        return None

# --- APP LOGIC ---
if 'active_video' not in st.session_state: st.session_state.active_video = None

st.title("🎵 Music Recommendation System")

# Load Data
if os.path.exists('SpotifySongs.csv'):
    df = pd.read_csv('SpotifySongs.csv')
    
    # Simple Mood Filter
    mood = st.selectbox("How are you feeling?", ["Happy", "Sad", "Romantic"])
    if mood == "Happy": f_df = df[df['Valence'] > 0.6]
    elif mood == "Sad": f_df = df[df['Valence'] < 0.4]
    else: f_df = df[(df['Valence'] > 0.4) & (df['Valence'] < 0.6)]

    # Display Player if active
    if st.session_state.active_video:
        st.markdown("### 🔊 Now Playing")
        v_id = st.session_state.active_video
        st.video(f"https://www.youtube.com/watch?v={v_id}")
        if st.button("❌ Close Player"):
            st.session_state.active_video = None
            st.rerun()

    st.write("---")
    
    # Display Songs
    for i, row in f_df.head(5).iterrows():
        st.markdown(f"""
            <div class="song-card">
                <b>{row['SongName']}</b><br><span style='opacity:0.6'>{row['ArtistName']}</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ Play {row['SongName']}", key=f"p_{i}"):
            vid = get_video_id(row['SongName'], row['ArtistName'])
            if vid:
                st.session_state.active_video = vid
                st.rerun()
            else:
                st.error("Could not find audio for this track.")

    st.markdown(f"<div class='footer-names'>Buddhadeb • Arghadeep • Sanajit • Kamalakanta</div>", unsafe_allow_html=True)
else:
    st.error("Please upload SpotifySongs.csv to GitHub.")

import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- THE ARTISTIC "IN-APP" MASTERPIECE ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. ARTISTIC ABSTRACT BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            linear-gradient(rgba(128, 128, 128, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 35px 35px, 35px 35px;
        background-attachment: fixed;
    }

    /* 3. NEON SEARCH & MOOD BOXES */
    .stTextInput input { 
        border-radius: 18px; border: 1px solid rgba(128,128,128,0.2); 
        padding: 15px; background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 10px; margin-top: 15px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.3s;
    }
    
    /* Mood Colors */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #00B4DB, #0083B0); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #141E30, #243B55); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #56ab2f, #a8e063); } 
    
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Tracks"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.05); border: 3px solid white !important; }

    /* 4. "NOW PLAYING" HUB */
    .now-playing-box {
        background: rgba(128, 128, 128, 0.1);
        border: 2px solid #1DB954;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 25px;
        backdrop-filter: blur(20px);
        text-align: center;
    }

    /* 5. SONG CARDS */
    .song-card {
        padding: 20px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
    }

    /* 6. TEAM FOOTER */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #00B4DB, #ff4e50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# State
if 'active_song' not in st.session_state: st.session_state.active_song = None
if 'display_count' not in st.session_state: st.session_state.display_count = 5

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.6;'>A Data-Driven Mood Discovery Engine</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset missing! Please ensure 'SpotifySongs.csv' is uploaded.")
    else:
        # --- THE SEPARATE PLAYER (HUB) ---
        if st.session_state.active_song:
            song = st.session_state.active_song
            st.markdown(f"""
                <div class="now-playing-box">
                    <h3 style="margin:0; color:#1DB954;">🔊 Now Playing</h3>
                    <p style="opacity:0.8; font-size:1.1rem;">{song['name']} • {song['artist']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Use a higher iframe to satisfy YouTube's security requirements
            search_query_encoded = urllib.parse.quote(f"{song['name']} {song['artist']} official audio")
            player_html = f"""
                <iframe width="100%" height="315" 
                src="https://www.youtube.com/embed?listType=search&list={search_query_encoded}&autoplay=1" 
                frameborder="0" allow="autoplay; encrypted-media" allowfullscreen 
                style="border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-top:-10px;"></iframe>
            """
            st.components.v1.html(player_html, height=330)
            if st.button("❌ Stop Music", use_container_width=True):
                st.session_state.active_song = None
                st.rerun()

        # --- FILTERS ---
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Pick Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # Filtering logic
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice != "All Songs":
            if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.45) | (f_df['Acousticness'] > 0.6)]
            elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.3) & (f_df['Valence'] < 0.7) & (f_df['Energy'] < 0.65)]
            elif mood_choice == "Happy/Energetic": f_df = f_df[(f_df['Valence'] > 0.6) | (f_df['Energy'] > 0.7)]

        # --- RESULTS ---
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.write(f"Discovery: **{len(recs)}** tracks found")
        
        for i in range(show_now):
            row = recs.iloc[i]
            with st.container():
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.3rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.6; font-size: 1rem;">Artist: {row['ArtistName']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"▶️ Play Track", key=f"btn_{i}", use_container_width=True):
                    st.session_state.active_song = {'name': row['SongName'], 'artist': row['ArtistName']}
                    st.rerun()
                st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 5
                st.rerun()

    # --- TEAM FOOTER ---
    st.markdown(f"""
        <div class="footer-container">
            <p style="color: grey; font-size: 0.7rem; letter-spacing: 3px; margin-bottom: 12px;">DEVELOPED BY</p>
            <div class="footer-names">
                Buddhadeb • Arghadeep • Sanajit • Kamalakanta
            </div>
            <p style="color: grey; font-size: 0.6rem; margin-top: 20px; opacity: 0.4;">© 2026 MoodTunes Project • CSE Dept</p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

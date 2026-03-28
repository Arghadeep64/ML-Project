import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- ADVANCED AESTHETIC UI CONFIG ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE STREAMLIT BRANDING */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. DYNAMIC ABSTRACT BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(29, 185, 84, 0.07) 0%, transparent 35%),
            radial-gradient(circle at 85% 85%, rgba(221, 36, 118, 0.07) 0%, transparent 35%),
            linear-gradient(rgba(128, 128, 128, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 30px 30px, 30px 30px;
        background-attachment: fixed;
    }

    /* 3. GLASSMORPHISM CARDS & BUTTONS */
    .stTextInput input { 
        border-radius: 20px; border: 1.5px solid rgba(128,128,128,0.2); 
        padding: 12px; background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 10px; margin-top: 10px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important;
        cursor: pointer; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    /* Mood Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #00B4DB, #0083B0); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #141E30, #243B55); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #56ab2f, #a8e063); } 
    
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Tracks"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.08); border: 2.5px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.2); }

    .song-card {
        padding: 20px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
    }
    
    /* 4. SEPARATE MEDIA PLAYER STYLING */
    .now-playing-container {
        background: rgba(29, 185, 84, 0.1);
        border: 1px solid #1DB954;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 30px;
        backdrop-filter: blur(20px);
        animation: slideDown 0.5s ease-out;
    }
    @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

    /* 5. FOOTER */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #00B4DB, #ff4e50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

# --- STATE MANAGEMENT ---
if 'playing_song' not in st.session_state: st.session_state.playing_song = None
if 'display_count' not in st.session_state: st.session_state.display_count = 10

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.6;'>Interactive Mood-Based Audio Engine</p>", unsafe_allow_html=True)
with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset missing! Please ensure 'SpotifySongs.csv' is uploaded.")
    else:
        # --- MEDIA PLAYER SECTION ---
        # This section only appears when a song is clicked
        if st.session_state.playing_song:
            song = st.session_state.playing_song
            st.markdown(f"""
                <div class="now-playing-container">
                    <h4 style="margin: 0; color: #1DB954;">🔊 Now Playing</h4>
                    <p style="margin-bottom: 15px; opacity: 0.8;">{song['name']} by {song['artist']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # The Player Embed (Hidden within the container space)
            search_slug = urllib.parse.quote(f"{song['name']} {song['artist']} official audio")
            player_html = f"""
                <iframe width="100%" height="160" 
                src="https://www.youtube.com/embed?listType=search&list={search_slug}&autoplay=1" 
                frameborder="0" allow="autoplay; encrypted-media" allowfullscreen 
                style="border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);"></iframe>
            """
            st.components.v1.html(player_html, height=170)
            if st.button("❌ Close Player", use_container_width=True):
                st.session_state.playing_song = None
                st.rerun()

        # --- FILTERS ---
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Select Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # Logic
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
                        <div style="font-weight: 800; font-size: 1.3rem;">{row['SongName']}</div>
                        <div style="opacity: 0.6;">Artist: {row['ArtistName']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # SEPARATE PLAY BUTTON
                if st.button(f"▶️ Play {row['SongName']}", key=f"play_{i}", use_container_width=True):
                    st.session_state.playing_song = {'name': row['SongName'], 'artist': row['ArtistName']}
                    st.rerun()
                st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 10
                st.rerun()

        # --- FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: grey; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 8px;">PROUDLY DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.6rem; margin-top: 15px; opacity: 0.4;">© 2026 MoodTunes Project • Built with Python</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

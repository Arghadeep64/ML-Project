import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- THE CREATIVE MASTERPIECE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT BRANDING */
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
            radial-gradient(circle at 50% 50%, rgba(128, 128, 128, 0.05) 0%, transparent 60%),
            linear-gradient(rgba(128, 128, 128, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        background-attachment: fixed;
    }

    /* 3. NEON SEARCH & MOOD BOXES */
    .stTextInput input { 
        border-radius: 20px; border: 1px solid rgba(128,128,128,0.2); 
        padding: 15px; background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 12px; margin-top: 15px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; font-size: 15px !important; color: white !important;
        cursor: pointer; transition: 0.4s ease;
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

    div[role="radiogroup"] [data-checked="true"] + div { 
        transform: scale(1.08); border: 3px solid white !important; 
        box-shadow: 0 0 25px rgba(255,255,255,0.3); 
    }

    /* 4. SONG CARD DESIGN */
    .song-card {
        padding: 30px; border-radius: 25px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
        transition: 0.3s;
    }
    .song-card:hover { border-color: #1DB954; transform: translateY(-5px); }

    /* 5. TEAM FOOTER (Professional spacing) */
    .footer-container {
        margin-top: 100px; padding: 60px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
        background: rgba(128, 128, 128, 0.02);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 6px; text-transform: uppercase; font-size: 1.4rem;
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

# State management
if 'display_count' not in st.session_state: st.session_state.display_count = 3

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.6; font-size: 1.1rem;'>Curated soundscapes based on audio features</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset missing! Please ensure 'SpotifySongs.csv' is in your GitHub folder.")
    else:
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Pick Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- ML FILTERING ---
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice != "All Songs":
            if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.45) | (f_df['Acousticness'] > 0.6)]
            elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.3) & (f_df['Valence'] < 0.7) & (f_df['Energy'] < 0.65)]
            elif mood_choice == "Happy/Energetic": f_df = f_df[(f_df['Valence'] > 0.6) | (f_df['Energy'] > 0.7)]

        # --- DISPLAY ---
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.info(f"Found **{len(recs)}** tracks. Displaying top results.")

        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Card
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 900; font-size: 1.6rem; color: #1DB954;">{row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 1.2rem; margin-bottom: 20px;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- THE "STABLE" IN-APP PLAYER ---
            # We use a YouTube Embed with a "Video Search" list to find the song
            search_slug = urllib.parse.quote(f"{row['SongName']} {row['ArtistName']} official audio")
            
            # This HTML uses a hidden search list to find the video without redirecting
            player_html = f"""
            <iframe width="100%" height="200" 
            src="https://www.youtube.com/embed?listType=search&list={search_slug}" 
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen 
            style="border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-top: -15px;">
            </iframe>
            """
            st.components.v1.html(player_html, height=210)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Recommendations", use_container_width=True):
                st.session_state.display_count += 3
                st.rerun()

    # --- TEAM FOOTER ---
    st.markdown(f"""
        <div class="footer-container">
            <p style="color: grey; font-size: 0.8rem; letter-spacing: 4px; margin-bottom: 15px;">PROJECT DEVELOPED BY</p>
            <div class="footer-names">
                Buddhadeb • Arghadeep • Sanajit • Kamalakanta
            </div>
            <p style="color: grey; font-size: 0.7rem; margin-top: 30px; opacity: 0.5;">© 2026 Music Recommendation System • CSE Dept</p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Something went wrong: {e}")

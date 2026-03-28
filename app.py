import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- CREATIVE & STABLE MASTERPIECE ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. ARTISTIC ABSTRACT BACKGROUND */
    /* Animated Mesh + Floating Neon Glows */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(29, 185, 84, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(221, 36, 118, 0.08) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.1) 1.5px, transparent 1.5px); /* Artistic Grid/Dots */
        background-size: 100% 100%, 100% 100%, 40px 40px;
        background-attachment: fixed;
        animation: subtleShift 20s infinite alternate;
    }
    
    @keyframes subtleShift {
        from { background-position: 0% 0%, 0% 0%, 0% 0%; }
        to { background-position: 5% 5%, -5% -5%, 10px 10px; }
    }

    /* 3. SEARCH & MOOD CARDS */
    .stTextInput input { 
        border-radius: 18px; border: 1px solid rgba(128,128,128,0.2); 
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

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.08); border: 3px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.3); }

    /* 4. SONG CARD DESIGN */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 5px;
        transition: 0.3s;
    }
    .song-card:hover { transform: translateY(-5px); border-color: #1DB954; }

    /* 5. TEAM FOOTER (No <br> used) */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 300; letter-spacing: 4px; text-transform: uppercase; font-size: 1.2rem;
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
if 'display_count' not in st.session_state: st.session_state.display_count = 5

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.6;'>A Data-Driven Mood Discovery Experience</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset missing! Please upload 'SpotifySongs.csv'.")
    else:
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Select Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- ML FILTERING LOGIC ---
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice != "All Songs":
            if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.45) | (f_df['Acousticness'] > 0.6)]
            elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.3) & (f_df['Valence'] < 0.7) & (f_df['Energy'] < 0.65)]
            elif mood_choice == "Happy/Energetic": f_df = f_df[(f_df['Valence'] > 0.6) | (f_df['Energy'] > 0.7)]

        # --- DISPLAY RESULTS ---
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.write(f"Discovery: **{len(recs)}** tracks found")
        
        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Card
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954;">{row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 1rem; margin-bottom: 15px;">Artist: {row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- THE STABLE PLAYER ---
            # Using a reliable HTTPS Search Embed
            search_slug = urllib.parse.quote(f"{row['SongName']} {row['ArtistName']}")
            # Standard Spotify Search URL for embedding
            embed_url = f"https://open.spotify.com/embed/search/{search_slug}"
            
            st.components.v1.iframe(embed_url, height=180)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 5
                st.rerun()

        # --- TEAM FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 12px;">PROUDLY DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.6rem; margin-top: 20px; opacity: 0.4;">© 2026 MoodTunes Project • Built with Python</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Logic Error: {e}")

import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- ULTRA-AESTHETIC & STABLE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. ARTISTIC ABSTRACT BACKGROUND */
    /* Moving Neon Glows and Floating Shapes */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.05), rgba(233, 64, 87, 0.05));
        background-size: 400% 400%;
        animation: gradientMove 20s ease infinite;
        background-attachment: fixed;
    }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: -10%; left: -10%; width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(29, 185, 84, 0.1) 0%, transparent 70%);
        filter: blur(80px); z-index: -1; animation: float 15s infinite alternate;
    }
    @keyframes gradientMove { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes float { 0% { transform: translate(0, 0); } 100% { transform: translate(100px, 50px); } }

    /* 3. NEON SEARCH & MOOD CARDS */
    .stTextInput input { 
        border-radius: 20px; border: 2px solid rgba(128,128,128,0.2); 
        padding: 15px; background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 12px; margin-top: 20px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; font-size: 15px !important; color: white !important;
        cursor: pointer; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.1); border: 3px solid white !important; box-shadow: 0 0 25px rgba(255,255,255,0.3); }

    /* 4. GLASSMORPHISM SONG CARDS */
    .song-card {
        padding: 30px; border-radius: 25px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 10px;
        transition: 0.4s;
    }
    .song-card:hover { border-color: #1DB954; transform: translateY(-5px); background: rgba(128, 128, 128, 0.1); }

    /* 5. DYNAMIC TEAM FOOTER */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.3rem;
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

if 'display_count' not in st.session_state: st.session_state.display_count = 5

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<h4 style='opacity: 0.6; font-weight: 300;'>Explore the rhythm of your mood</h4>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search songs or artists...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ CSV Dataset missing! Please upload 'SpotifySongs.csv' to GitHub.")
    else:
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Select Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC ---
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
        
        st.info(f"Discovery: **{len(recs)}** tracks found for this mood.")

        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Glass Card
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 900; font-size: 1.5rem; color: #1DB954;">{row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 1.1rem; margin-bottom: 15px;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- THE STABLE IN-APP PLAYER ---
            # Spotify Search Widget is much more stable than YouTube Search for iframes
            search_slug = urllib.parse.quote(f"{row['SongName']} {row['ArtistName']}")
            embed_url = f"https://open.spotify.com/embed/search/{search_slug}"
            
            st.components.v1.iframe(embed_url, height=180)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 5
                st.rerun()

        # --- PROFESSIONAL FOOTER ---
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
    st.error(f"Error: {e}")

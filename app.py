import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- ULTRA-STABLE CREATIVE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. DYNAMIC NEON MESH BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.07), rgba(42, 82, 152, 0.07), rgba(233, 64, 87, 0.07));
        background-size: 400% 400%;
        animation: gradientMove 20s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 3. NEON SEARCH & MOOD BOXES */
    .stTextInput input { 
        border-radius: 15px; 
        border: 1px solid rgba(128,128,128,0.2); 
        padding: 12px; 
        background: rgba(255, 255, 255, 0.05) !important;
        transition: 0.3s;
    }
    .stTextInput input:focus { border-color: #1DB954; box-shadow: 0 0 15px rgba(29, 185, 84, 0.2); }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 10px; width: 100%; margin-top: 10px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 700; font-size: 14px !important; color: white !important;
        cursor: pointer; transition: 0.4s;
    }
    
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #00B4DB, #0083B0); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #141E30, #243B55); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #56ab2f, #a8e063); } 
    
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Tracks"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.08); border: 3px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.2); }

    /* 4. CREATIVE SONG CARDS */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 5px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .song-card:hover { transform: translateY(-5px); background: rgba(128, 128, 128, 0.1); border-color: #1DB954; }

    /* 5. FOOTER */
    .footer-container {
        margin-top: 100px; padding: 50px;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
        text-align: center;
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem;
        background: linear-gradient(to right, #00B4DB, #ff4e50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        df = pd.read_csv('SpotifySongs.csv')
        # Clean potential NaNs to prevent crashes
        df['SongName'] = df['SongName'].fillna("Unknown Track")
        df['ArtistName'] = df['ArtistName'].fillna("Unknown Artist")
        return df
    return pd.DataFrame()

# State management
if 'display_count' not in st.session_state: st.session_state.display_count = 20

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.6;'>A modern mood-based discovery engine</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    
    if df.empty:
        st.error("⚠️ Error: 'SpotifySongs.csv' not found in your GitHub repository. Please upload it!")
    else:
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Select Your Vibe")
        mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- RECOMENDATION LOGIC ---
        f_df = df.copy()
        
        # 1. Search filter
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].str.lower().str.contains(q, na=False)]

        # 2. Mood filter
        if mood_choice != "All Songs":
            if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.45) | (f_df['Acousticness'] > 0.6)]
            elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.3) & (f_df['Valence'] < 0.7) & (f_df['Energy'] < 0.65)]
            elif mood_choice == "Happy/Energetic": f_df = f_df[(f_df['Valence'] > 0.6) | (f_df['Energy'] > 0.7)]

        # --- DISPLAY RESULTS ---
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Tracks Found", len(recs))
        c2.metric("Showing", show_now)
        c3.metric("Mood", mood_choice.split('/')[0])

        st.write("---")

        for i in range(show_now):
            row = recs.iloc[i]
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954;">{row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 1rem; margin-bottom: 15px;">Artist: {row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # THE PLAY BUTTON (Creative Search)
            # Instead of iframe, we use a beautifully styled link button
            search_url = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
            st.link_button(f"▶️ Play {row['SongName']} on Spotify", search_url, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Discover More tracks", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

        # --- FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 12px;">PROUDLY DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.6rem; margin-top: 20px; opacity: 0.4;">© 2026 MoodTunes Project • Built with Python & Streamlit</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Logic Error: {e}")

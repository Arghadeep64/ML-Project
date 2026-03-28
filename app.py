import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- MASTERPIECE UI CONFIG ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. CLEAN THEME & ADAPTIVE BACKDROP */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: block !important;} /* Keeps the settings menu for Light/Dark toggle */

    /* 2. MODERN SMOOTH BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 40%),
            radial-gradient(rgba(128, 128, 128, 0.05) 1.5px, transparent 1.5px);
        background-size: 100% 100%, 100% 100%, 40px 40px;
        background-attachment: fixed;
    }

    /* 3. ENTRANCE ANIMATIONS */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-container {
        animation: fadeInUp 0.8s ease-out;
    }

    /* 4. GLASSMORPHISM SEARCH & MOOD SELECTOR */
    .stTextInput input { 
        border-radius: 20px; 
        border: 1px solid rgba(128,128,128,0.2); 
        padding: 15px; 
        background: rgba(128, 128, 128, 0.05) !important;
        backdrop-filter: blur(10px);
        transition: 0.3s;
    }
    .stTextInput input:focus { border-color: #1DB954; box-shadow: 0 0 15px rgba(29, 185, 84, 0.2); }
    
    div[role="radiogroup"] { display: flex; flex-wrap: wrap !important; justify-content: center; gap: 12px; margin-top: 15px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; min-width: 120px; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer; 
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    /* Elegant Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #667eea, #764ba2); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #2b5876, #4e4376); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff0844, #ffb199); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #0ba360, #3cba92); } 
    div[role="radiogroup"] label:nth-of-type(5) { background: linear-gradient(135deg, #FF512F, #DD2476); } 
    div[role="radiogroup"] label:nth-of-type(6) { background: linear-gradient(135deg, #4b6cb7, #182848); } 
    div[role="radiogroup"] label:nth-of-type(7) { background: linear-gradient(135deg, #00d2ff, #3a7bd5); } 
    div[role="radiogroup"] label:nth-of-type(8) { background: linear-gradient(135deg, #f80759, #bc4e9c); } 
    
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "Everything"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Workout"; }
    div[role="radiogroup"] label:nth-of-type(5)::after { content: "Party"; }
    div[role="radiogroup"] label:nth-of-type(6)::after { content: "Focus"; }
    div[role="radiogroup"] label:nth-of-type(7)::after { content: "Chill"; }
    div[role="radiogroup"] label:nth-of-type(8)::after { content: "Dance"; }

    div[role="radiogroup"] [data-checked="true"] + div { transform: scale(1.1); border: 3px solid white !important; box-shadow: 0 0 20px rgba(255,255,255,0.2); }

    /* 5. FLAWLESS SONG CARDS */
    .song-card {
        padding: 30px; border-radius: 25px;
        background: rgba(128, 128, 128, 0.05); 
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1); 
        margin-bottom: 10px;
        transition: 0.4s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    .song-card:hover { transform: translateY(-5px); border-color: #1DB954; background: rgba(128, 128, 128, 0.08); }

    /* 6. TEAM FOOTER */
    .footer-container {
        margin-top: 100px; padding: 60px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.3rem;
        background: linear-gradient(to right, #667eea, #ff0844);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    if os.path.exists('SpotifySongs.csv'):
        return pd.read_csv('SpotifySongs.csv')
    return pd.DataFrame()

if 'display_count' not in st.session_state:
    st.session_state.display_count = 20

# --- HEADER SECTION ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.8; font-size: 1.2rem; font-weight: 300; text-align: center;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # Search Box
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        # Mood Selection
        mood_choices = ["All", "Sad", "Romantic", "Gym", "Party", "Study", "Chill", "Dance"]
        st.write("### ✨ Match your Mood")
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC (UNTOUCHED) ---
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        if mood_choice == "Sad": f_df = f_df[(f_df['Valence'] < 0.4)]
        elif mood_choice == "Romantic": f_df = f_df[(f_df['Valence'] > 0.4) & (f_df['Valence'] < 0.6) & (f_df['Energy'] < 0.6)]
        elif mood_choice == "Gym": f_df = f_df[(f_df['Energy'] > 0.7) & (f_df['Tempo'] > 115)]
        elif mood_choice == "Party": f_df = f_df[(f_df['Danceability'] > 0.7) & (f_df['Energy'] > 0.7)]
        elif mood_choice == "Study": f_df = f_df[(f_df['Instrumentalness'] > 0.4) | (f_df['Energy'] < 0.5)]
        elif mood_choice == "Chill": f_df = f_df[(f_df['Energy'] < 0.4) & (f_df['Loudness'] < -10)]
        elif mood_choice == "Dance": f_df = f_df[(f_df['Danceability'] > 0.8)]

        # --- TRACK COUNTER ---
        st.metric(label="Songs Found", value=len(f_df))
        st.write("---")

        # --- DISPLAY ---
        if f_df.empty:
            st.warning("No songs found for this selection.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 900; font-size: 1.5rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.6; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                        <div style="margin-top: 15px;">
                            <span style="background: rgba(29, 185, 84, 0.2); padding: 5px 15px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                u = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)
                st.write("")

            if show_now < len(recs):
                if st.button("⬇️ Show More Songs", use_container_width=True):
                    st.session_state.display_count += 20
                    st.rerun()

        # --- TEAM FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 15px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 25px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
st.markdown('</div>', unsafe_allow_html=True)

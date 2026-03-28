import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- ARTISTIC MUSIC APP UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. ANIMATED DYNAMIC BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.03), rgba(42, 82, 152, 0.03), rgba(233, 64, 87, 0.03));
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. SEARCH & MOOD BOXES */
    .stTextInput input { border-radius: 12px; border: 1px solid rgba(128,128,128,0.2); padding: 12px; }
    
    div[role="radiogroup"] { display: flex; flex-wrap: wrap !important; justify-content: flex-start; gap: 10px; width: 100%; margin-top: 10px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; min-width: 120px; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; font-size: 14px !important; color: white !important;
        cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Vibrant Mood Gradients */
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

    div[role="radiogroup"] [data-checked="true"] + div { border: 3px solid white !important; transform: scale(1.05); }

    /* 3. SONG CARDS */
    .song-card {
        padding: 20px; border-radius: 15px;
        background: rgba(128, 128, 128, 0.08); backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 10px;
        transition: 0.3s;
    }
    .song-card:hover { transform: translateX(10px); background: rgba(128, 128, 128, 0.12); border-color: #1DB954; }

    /* 4. TEAM FOOTER */
    .footer-container {
        margin-top: 100px; padding: 40px; border-radius: 30px 30px 0 0;
        background: rgba(128, 128, 128, 0.05); border-top: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
    }
    .footer-names {
        font-weight: 200; letter-spacing: 4px; text-transform: uppercase; font-size: 1.2rem;
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

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<p style='opacity: 0.8; font-size: 1.1rem; font-weight: 300;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found. Please upload 'SpotifySongs.csv'.")
    else:
        # Renamed section
        mood_choices = ["All", "Sad", "Romantic", "Gym", "Party", "Study", "Chill", "Dance"]
        st.write("### ✨ Match your Mood")
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC ---
        f_df = df.copy()
        if search_query.strip():
            q = search_query.strip().lower()
            f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                        f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        # Recommendation Logic
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

        # --- RESULTS ---
        if f_df.empty:
            st.warning("No songs found for this selection.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.3rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.7; font-size: 1rem;">{row['ArtistName']}</div>
                        <div style="margin-top: 10px;">
                            <span style="background: rgba(29, 185, 84, 0.2); padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Dynamic Search Link
                u = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
                st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)
                st.write("")

            if show_now < len(recs):
                if st.button("⬇️ Show More Songs", use_container_width=True):
                    st.session_state.display_count += 20
                    st.rerun()

        # --- TEAM FOOTER ---
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 10px;">DEVELOPED BY</p>
                <div class="footer-names">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: grey; font-size: 0.7rem; margin-top: 20px; opacity: 0.5;">© 2026 MOODTUNES PROJECT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

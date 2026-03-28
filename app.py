import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- MODERN GRID DESIGN UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. ANIMATED DYNAMIC BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.04), rgba(42, 82, 152, 0.04), rgba(233, 64, 87, 0.04));
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 3. SEARCH & MOOD BOXES */
    .stTextInput input { 
        border-radius: 25px; 
        border: 1px solid rgba(128,128,128,0.2); 
        padding: 15px; 
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: wrap !important; justify-content: center; gap: 12px; margin-top: 20px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; min-width: 130px; height: 55px; display: flex; align-items: center; justify-content: center;
        border-radius: 15px; font-weight: 800; color: white !important; cursor: pointer; transition: 0.4s;
    }
    
    /* Vibrant Mood Gradients - EXACTLY SAME ORDER */
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

    /* 4. MODERN SONG CARDS (GRID VERSION) */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.05); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 5px;
        transition: 0.4s; height: 160px; display: flex; flex-direction: column; justify-content: center;
    }
    .song-card:hover { transform: translateY(-5px); border-color: #1DB954; background: rgba(128, 128, 128, 0.08); }

    /* 5. TEAM FOOTER */
    .footer-container {
        margin-top: 120px; padding: 60px; text-align: center;
        border-top: 1px solid rgba(128, 128, 128, 0.1);
    }
    .footer-names {
        font-weight: 200; letter-spacing: 5px; text-transform: uppercase; font-size: 1.3rem;
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
st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.8; font-size: 1.2rem; font-weight: 300; text-align: center;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ Dataset not found.")
    else:
        # SEARCH & MOOD CONTROLS
        c_search, _ = st.columns([2, 2])
        with c_search:
            search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        mood_choices = ["All", "Sad", "Romantic", "Gym", "Party", "Study", "Chill", "Dance"]
        st.write("### ✨ Match your Mood")
        mood_choice = st.radio("Mood Selector:", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # --- LOGIC (KEEPING EVERYTHING SAME) ---
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

        # --- GRID-BASED RESULTS ---
        if f_df.empty:
            st.warning("No songs found for this selection.")
        else:
            recs = f_df.reset_index(drop=True)
            show_now = min(st.session_state.display_count, len(recs))
            
            # Use columns to create the 2-column grid layout
            for i in range(0, show_now, 2):
                col1, col2 = st.columns(2)
                
                # Column 1 Track
                with col1:
                    row = recs.iloc[i]
                    st.markdown(f"""
                        <div class="song-card">
                            <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954; line-height: 1.2;">{row['SongName']}</div>
                            <div style="opacity: 0.7; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                            <div style="margin-top: 15px;">
                                <span style="background: rgba(29, 185, 84, 0.2); padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    u = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                    st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)

                # Column 2 Track (if it exists)
                if i + 1 < show_now:
                    with col2:
                        row = recs.iloc[i+1]
                        st.markdown(f"""
                            <div class="song-card">
                                <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954; line-height: 1.2;">{row['SongName']}</div>
                                <div style="opacity: 0.7; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                                <div style="margin-top: 15px;">
                                    <span style="background: rgba(29, 185, 84, 0.2); padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        u = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                        st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)
                st.write("")

            if show_now < len(recs):
                st.write("")
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

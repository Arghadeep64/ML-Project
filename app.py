import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse
import os

# --- NO-TELEPORT CREATIVE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT BRANDING */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* 2. DYNAMIC NEON MESH BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.05), rgba(233, 64, 87, 0.05));
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 3. NEON SEARCH & MOOD BOXES */
    .stTextInput input { 
        border-radius: 15px; border: 1px solid rgba(128,128,128,0.2); 
        padding: 12px; background: rgba(255, 255, 255, 0.05) !important;
    }
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 10px; width: 100%; margin-top: 10px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; font-size: 14px !important; color: white !important;
        cursor: pointer; transition: 0.3s;
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

    /* 4. SONG CARDS */
    .song-card {
        padding: 20px; border-radius: 20px;
        background: rgba(128, 128, 128, 0.08); backdrop-filter: blur(12px);
        border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 8px;
    }

    /* 5. FOOTER */
    .footer-container {
        margin-top: 80px; padding: 40px; border-top: 1px solid rgba(128, 128, 128, 0.1); text-align: center;
    }
    .footer-names {
        font-weight: 300; letter-spacing: 4px; text-transform: uppercase; font-size: 1.1rem;
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

if 'display_count' not in st.session_state:
    st.session_state.display_count = 5 # Small number for faster loading

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.caption("A modern vibe-based discovery engine")

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    if df.empty:
        st.error("⚠️ CSV file not found!")
    else:
        mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
        st.write("### ✨ Pick Your Vibe")
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

        # --- RESULTS ---
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.info(f"Discovery: **{len(recs)}** tracks match your mood.")
        
        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Card
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 800; font-size: 1.3rem; color: #1DB954;">{row['SongName']}</div>
                    <div style="opacity: 0.6; margin-bottom: 15px;">Artist: {row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # --- THE BUILT-IN PLAYER ---
            # This embeds a YouTube search result player. It stays INSIDE the app!
            search_query_encoded = urllib.parse.quote(f"{row['SongName']} {row['ArtistName']} official audio")
            # Using a custom HTML component for the player to ensure it stays in the app
            player_html = f"""
            <iframe width="100%" height="150" src="https://www.youtube.com/embed?listType=search&list={search_query_encoded}" 
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen style="border-radius:15px; margin-top:-10px; margin-bottom:20px;"></iframe>
            """
            st.components.v1.html(player_html, height=160)

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 5
                st.rerun()

    # --- TEAM FOOTER ---
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

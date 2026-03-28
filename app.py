import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse

# --- 1. [TEAM MEMBER: ARGHADEEP] UI/UX DESIGN & CSS ARCHITECTURE ---
# Responsibility: Crafting the visual identity, Dark Mode CSS, and Animations.

st.set_page_config(page_title="MoodTunes Music System", layout="wide")

# Permanent Dark Mode CSS with Glassmorphism
st.markdown("""
    <style>
    /* HIDE STREAMLIT OVERLAYS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

    /* DARK THEME BASE */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 90% 80%, rgba(221, 36, 118, 0.1) 0%, transparent 45%),
            radial-gradient(rgba(255, 255, 255, 0.05) 1.5px, transparent 1.5px);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* TYPOGRAPHY */
    h1, h2, h3, p, span, label, .stMetric div {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    /* SEARCH INPUT */
    .stTextInput input { 
        border-radius: 15px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        padding: 12px !important; 
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
    }

    /* PLAY BUTTONS (SPOTIFY STYLE) */
    [data-testid="stLinkButton"] a {
        background-color: #1DB954 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
        padding: 12px !important;
        transition: 0.3s ease !important;
    }
    [data-testid="stLinkButton"] a:hover {
        background-color: #1ed760 !important;
        transform: scale(1.02);
    }

    /* MOOD SELECTOR */
    div[role="radiogroup"] { display: flex; flex-wrap: wrap !important; gap: 8px; margin-top: 10px; }
    div[role="radiogroup"] label {
        padding: 0px 15px; min-width: 110px; height: 48px; 
        display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; color: white !important; cursor: pointer; 
    }
    div[role="radiogroup"] [data-checked="true"] + div { 
        transform: scale(1.05); border: 2.5px solid white !important;
    }

    /* SONG CARDS */
    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
        transition: 0.3s ease;
    }
    .song-card:hover { border-color: #1DB954; }

    /* FOOTER */
    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. [TEAM MEMBER: BUDDHADEB] DATA PROCESSING & CACHING ---
# Responsibility: Handling the Spotify dataset, cleaning null values, and optimizing load times.

@st.cache_data
def load_and_clean_data():
    if os.path.exists('SpotifySongs.csv'):
        data = pd.read_csv('SpotifySongs.csv')
        return data.dropna()
    return pd.DataFrame()

# --- 3. [TEAM MEMBER: SANAJIT] FEATURE ENGINEERING & MOOD LOGIC ---
# Responsibility: Developing the algorithms that map audio features (Valence, Energy, Tempo) to human moods.

def filter_by_mood(df, mood):
    if mood == "Sad": return df[df['Valence'] < 0.4]
    elif mood == "Romantic": return df[(df['Valence'] > 0.4) & (df['Valence'] < 0.6) & (df['Energy'] < 0.6)]
    elif mood == "Workout": return df[(df['Energy'] > 0.7) & (df['Tempo'] > 115)]
    elif mood == "Party": return df[(df['Danceability'] > 0.7) & (df['Energy'] > 0.7)]
    elif mood == "Focus": return df[(df['Instrumentalness'] > 0.4) | (df['Energy'] < 0.5)]
    elif mood == "Chill": return df[(df['Energy'] < 0.4) & (df['Loudness'] < -10)]
    elif mood == "Dance": return df[df['Danceability'] > 0.8]
    return df

# --- 4. [TEAM MEMBER: KAMALAKANTA] SYSTEM INTEGRATION & DEPLOYMENT ---
# Responsibility: Managing state, implementing search functionality, and coordinating the final deployment.

if 'display_limit' not in st.session_state: st.session_state.display_limit = 20

st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.7; font-size: 1.1rem; font-weight: 300; margin-top: -15px;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_and_clean_data()
    if df.empty:
        st.error("⚠️ Dataset not found. Please upload 'SpotifySongs.csv'.")
    else:
        # Search & Mood Section
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        st.write("### ✨ Match your Mood")
        mood_choices = ["All Songs", "Sad", "Romantic", "Workout", "Party", "Focus", "Chill", "Dance"]
        
        # Mapping gradients to Moods (Arghadeep's CSS logic continues here)
        st.markdown("""
            <style>
            div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #667eea, #764ba2); } 
            div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #2b5876, #4e4376); } 
            div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
            div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #0ba360, #3cba92); } 
            div[role="radiogroup"] label:nth-of-type(5) { background: linear-gradient(135deg, #FF512F, #DD2476); } 
            div[role="radiogroup"] label:nth-of-type(6) { background: linear-gradient(135deg, #4b6cb7, #182848); } 
            div[role="radiogroup"] label:nth-of-type(7) { background: linear-gradient(135deg, #00d2ff, #3a7bd5); } 
            div[role="radiogroup"] label:nth-of-type(8) { background: linear-gradient(135deg, #f80759, #bc4e9c); } 
            </style>
        """, unsafe_allow_html=True)
        
        mood_choice = st.radio("Mood Selector", options=mood_choices, horizontal=True, label_visibility="collapsed")

        # Filtering Logic
        filtered_df = filter_by_mood(df, mood_choice)
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[filtered_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                                    filtered_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        st.metric(label="Songs Found", value=len(filtered_df))
        st.write("---")

        if filtered_df.empty:
            st.warning("No songs found for this selection.")
        else:
            recs = filtered_df.reset_index(drop=True)
            show_now = min(st.session_state.display_limit, len(recs))
            
            for i in range(show_now):
                row = recs.iloc[i]
                st.markdown(f"""
                    <div class="song-card">
                        <div style="font-weight: 800; font-size: 1.4rem; color: #1DB954;">{row['SongName']}</div>
                        <div style="opacity: 0.6; font-size: 1.1rem; margin-top: 5px;">{row['ArtistName']}</div>
                        <div style="margin-top: 12px;">
                            <span style="background: rgba(29, 185, 84, 0.2); color: #1DB954; padding: 5px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">🔥 {row['Popularity']}% Trending</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                u = f"https://open.spotify.com/search/{urllib.parse.quote(row['SongName'] + ' ' + row['ArtistName'])}"
                st.link_button(f"▶️ Listen to {row['SongName']}", u, use_container_width=True)
                st.write("")

            if show_now < len(recs):
                if st.button("⬇️ Show More Songs", use_container_width=True):
                    st.session_state.display_limit += 20
                    st.rerun()

        # Final Branding & Team Credits
        st.markdown(f"""
            <div class="footer-container">
                <p style="color: rgba(255,255,255,0.4); font-size: 0.8rem; letter-spacing: 4px; margin-bottom: 12px;">DEVELOPED BY</p>
                <div style="font-weight: 300; letter-spacing: 5px; text-transform: uppercase; font-size: 1.2rem; background: linear-gradient(to right, #667eea, #ff4e50); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Buddhadeb • Arghadeep • Sanajit • Kamalakanta
                </div>
                <p style="color: rgba(255,255,255,0.2); font-size: 0.75rem; margin-top: 25px;">© 2026 MOODTUNES PROJECT • CSE DEPARTMENT</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"System Error: {e}")

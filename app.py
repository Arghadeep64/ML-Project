import streamlit as st
import pandas as pd
import numpy as np

# --- CREATIVE MASTERPIECE UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. ARTISTIC FLOATING BACKGROUND */
    /* Creates blurred neon circles that float in the background */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 10%; left: 10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(29, 185, 84, 0.15) 0%, transparent 70%);
        filter: blur(50px);
        z-index: -1;
        animation: float 20s infinite alternate;
    }
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        bottom: 10%; right: 10%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(221, 36, 118, 0.15) 0%, transparent 70%);
        filter: blur(60px);
        z-index: -1;
        animation: float 25s infinite alternate-reverse;
    }

    @keyframes float {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 100px); }
    }

    /* 2. THE GRID PATTERN */
    [data-testid="stAppViewContainer"] {
        background-image: radial-gradient(rgba(128, 128, 128, 0.1) 1.5px, transparent 1.5px);
        background-size: 40px 40px;
        background-attachment: fixed;
    }

    /* 3. MODERN SEARCH BAR */
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        font-size: 16px;
    }

    /* 4. SLEEK MOOD BOXES */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: nowrap !important;
        justify-content: space-between;
        gap: 15px;
        margin-top: 20px;
    }

    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }

    div[role="radiogroup"] label {
        flex: 1;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        font-weight: 800;
        font-size: 16px !important;
        color: white !important;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Vibrant Mood Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #00B4DB, #0083B0); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #141E30, #243B55); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff4e50, #f9d423); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #56ab2f, #a8e063); } 

    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    /* Selection Glow */
    div[role="radiogroup"] [data-checked="true"] + div {
        transform: scale(1.1);
        box-shadow: 0 0 25px currentColor;
        border: 3px solid white !important;
    }

    /* 5. NEON SONG CARDS */
    .song-card {
        padding: 30px;
        border-radius: 25px;
        background: rgba(128, 128, 128, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        transition: all 0.4s ease;
    }
    .song-card:hover {
        border-color: #1DB954;
        box-shadow: 0 0 20px rgba(29, 185, 84, 0.2);
        background: rgba(128, 128, 128, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('SpotifySongs.csv')

if 'display_count' not in st.session_state:
    st.session_state.display_count = 20

# --- HEADER SECTION ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.markdown("<h4 style='opacity: 0.6; font-weight: 300;'>Explore the rhythm of your mood</h4>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search songs or artists...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    
    st.write("### ✨ Choose Your Vibe")
    mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

    # --- FILTERING LOGIC ---
    f_df = df.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                    f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

    if mood_choice != "All Songs":
        if mood_choice == "Sad": 
            f_df = f_df[(f_df['Valence'] < 0.45) | (f_df['Acousticness'] > 0.6)]
        elif mood_choice == "Romantic": 
            f_df = f_df[(f_df['Valence'] > 0.3) & (f_df['Valence'] < 0.7) & (f_df['Energy'] < 0.65)]
        elif mood_choice == "Happy/Energetic": 
            f_df = f_df[(f_df['Valence'] > 0.6) | (f_df['Energy'] > 0.7)]

    # --- RESULTS ---
    st.write("")
    if f_df.empty:
        st.warning("No matches found. Try clearing your search or picking a new mood!")
    else:
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.write(f"Current Discovery: **{len(recs)}** tracks")
        
        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Card
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 900; font-size: 1.4rem;">{row['SongName']}</div>
                    <div style="color: #1DB954; font-weight: 600;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Button
            spotify_url = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
            st.link_button(f"▶️ Play {row['SongName']}", spotify_url, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # --- RESTORED FOOTER WITH ALL NAMES ---
    st.markdown("<br><br><br>")
    st.divider()
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <p style='color: grey; font-size: 1rem; letter-spacing: 2px;'>DEVELOPED BY</p>
            <h3 style='font-weight: 200;'>Buddhadeb, Arghadeep, Sanajit, & Kamalakanta</h3>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Error loading music data: {e}")

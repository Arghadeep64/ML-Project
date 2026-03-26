import streamlit as st
import pandas as pd
import numpy as np

# --- ULTRA-AESTHETIC ANIMATED UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. ANIMATED MESH BACKGROUND */
    /* This creates a moving, artistic background that adapts to Light/Dark mode */
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, rgba(30, 60, 114, 0.05), rgba(42, 82, 152, 0.05), rgba(233, 64, 87, 0.05), rgba(242, 113, 33, 0.05));
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        background-attachment: fixed;
    }

    /* 2. ENTRANCE ANIMATIONS */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 3. SEARCH BOX - Soft Glass Look */
    .stTextInput input {
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 12px;
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #1DB954;
        box-shadow: 0 0 10px rgba(29, 185, 84, 0.2);
    }

    /* 4. SLEEK COMPACT MOOD CARDS */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: nowrap !important;
        justify-content: space-between;
        gap: 12px;
        width: 100%;
        margin-top: 15px;
    }

    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }

    div[role="radiogroup"] label {
        flex: 1;
        height: 55px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        font-weight: 700;
        font-size: 15px !important;
        color: white !important;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        white-space: nowrap;
        border: none !important;
    }

    /* Animated Gradients for Moods */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(45deg, #00c6ff, #0072ff); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(45deg, #3a1c71, #d76d77, #ffaf7b); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(45deg, #ee9ca7, #ffdde1); color: #444 !important; } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(45deg, #11998e, #38ef7d); } 

    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    /* Floating Selection effect */
    div[role="radiogroup"] [data-checked="true"] + div {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 12px 20px rgba(0,0,0,0.2);
        border: 2px solid white !important;
    }

    /* 5. SONG CARD DESIGN - Modern Glass */
    .song-card {
        padding: 25px;
        border-radius: 20px;
        background: rgba(128, 128, 128, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 15px;
        animation: fadeInUp 0.6s ease backwards;
        transition: all 0.3s ease;
    }
    .song-card:hover {
        background: rgba(128, 128, 128, 0.1);
        transform: scale(1.01);
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
    st.title("🎵 MoodTunes")
    st.markdown("<p style='opacity: 0.7; font-style: italic;'>Your Vibe, Your Music</p>", unsafe_allow_html=True)

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    
    st.write("### ✨ Select Mood")
    mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

    # --- FILTERING ---
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
        st.warning("No tracks found. Try a different search!")
    else:
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.write(f"Discovery: **{len(recs)}** songs")
        
        for i in range(show_now):
            row = recs.iloc[i]
            # Aesthetic Song Card
            st.markdown(f"""
                <div class="song-card" style="animation-delay: {i*0.05}s;">
                    <div style="font-weight: 800; font-size: 1.25rem;">{row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 1rem; margin-bottom: 15px;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Button
            spotify_link = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
            st.link_button(f"▶️ Play Now", spotify_link, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Discover More", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # --- FOOTER ---
    st.markdown("<br><hr><p style='text-align: center; color: grey; font-size: 0.85rem; letter-spacing: 1px;'>DESIGNED BY THE MOODTUNES TEAM</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"System Error: {e}")

import streamlit as st
import pandas as pd
import numpy as np

# --- ARTISTIC ABSTRACT UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. THE ABSTRACT BACKGROUND DESIGN */
    [data-testid="stAppViewContainer"] {
        background-color: transparent;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(29, 185, 84, 0.08) 0%, transparent 25%),
            radial-gradient(circle at 85% 15%, rgba(221, 36, 118, 0.08) 0%, transparent 25%),
            radial-gradient(circle at 50% 80%, rgba(255, 177, 153, 0.08) 0%, transparent 30%),
            radial-gradient(rgba(128, 128, 128, 0.1) 1px, transparent 1px); 
        background-size: 100% 100%, 100% 100%, 100% 100%, 30px 30px;
        background-attachment: fixed;
    }

    /* 2. SEARCH BOX STYLING */
    .stTextInput input {
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 12px;
        background: rgba(128, 128, 128, 0.05) !important;
    }

    /* 3. SLEEK COMPACT MOOD CARDS */
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
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-weight: 700;
        font-size: 15px !important;
        color: white !important;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        white-space: nowrap;
    }

    /* Vibrant Mood Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #667eea, #764ba2); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #2b5876, #4e4376); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff0844, #ffb199); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #0ba360, #3cba92); } 

    /* Text Labels */
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    div[role="radiogroup"] [data-checked="true"] + div {
        border: 3px solid white !important;
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }

    /* 4. SONG CARD DESIGN */
    .song-card {
        padding: 20px;
        border-radius: 18px;
        background: rgba(128, 128, 128, 0.08); 
        backdrop-filter: blur(5px);
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .song-card:hover {
        background: rgba(128, 128, 128, 0.15);
        transform: translateX(5px);
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
    # "Intelligent" removed below
    st.markdown("*Music Recommendation System*")

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search songs or artists...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    
    st.write("### ✨ Pick Your Vibe")
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
        
        st.write(f"Found **{len(recs)}** tracks for you")
        
        for i in range(show_now):
            row = recs.iloc[i]
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 800; font-size: 1.2rem; margin-bottom: 2px;">{i+1}. {row['SongName']}</div>
                    <div style="opacity: 0.6; font-size: 0.95rem; font-weight: 500;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            spotify_search = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
            st.link_button(f"▶️ Listen to {row['SongName']}", spotify_search, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More Tracks", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # --- FINAL FOOTER ---
    st.markdown("<br><hr><p style='text-align: center; color: grey; font-size: 0.85rem;'>Developed by: Buddhadeb, Arghadeep, Sanajit, & Kamalakanta</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Error: Please ensure 'SpotifySongs.csv' is in your GitHub folder. ({e})")

import streamlit as st
import pandas as pd
import numpy as np

# --- AESTHETIC MASTERPIECE UI ---
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
    
    div[role="radiogroup"] { display: flex; flex-wrap: nowrap !important; justify-content: space-between; gap: 10px; width: 100%; margin-top: 10px; }
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; font-size: 14px !important; color: white !important;
        cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Unique Mood Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #667eea, #764ba2); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #2b5876, #4e4376); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #ff0844, #ffb199); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #0ba360, #3cba92); } 
    
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    div[role="radiogroup"] [data-checked="true"] + div { border: 3px solid white !important; transform: scale(1.05); }

    /* 3. SONG CARDS */
    .song-card {
        padding: 20px; border-radius: 15px;
        background: rgba(128, 128, 128, 0.08); backdrop-filter: blur(10px);
        border: 1px solid rgba(128, 128, 128, 0.1); margin-bottom: 10px;
        transition: 0.3s;
    }
    .song-card:hover { transform: translateX(10px); background: rgba(128, 128, 128, 0.12); }

    /* 4. CREATIVE FOOTER (No more <br> needed) */
    .footer-container {
        margin-top: 100px; /* This creates the professional space */
        padding: 40px;
        border-radius: 30px 30px 0 0;
        background: rgba(128, 128, 128, 0.05);
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
    }
    .footer-names {
        font-weight: 200;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-size: 1.2rem;
        background: linear-gradient(to right, #667eea, #ff0844);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('SpotifySongs.csv')

if 'display_count' not in st.session_state:
    st.session_state.display_count = 20

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t:
    st.title("🎵 Music Recommendation System")
    st.caption("Discover your sound by mood and artist")

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    
    st.write("### ✨ Select Mood")
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
    if f_df.empty:
        st.warning("No matches found.")
    else:
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        for i in range(show_now):
            row = recs.iloc[i]
            st.markdown(f"""
                <div class="song-card">
                    <div style="font-weight: 800; font-size: 1.2rem;">{row['SongName']}</div>
                    <div style="opacity: 0.6;">{row['ArtistName']}</div>
                </div>
            """, unsafe_allow_html=True)
            u = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
            st.link_button(f"▶️ Play {row['SongName']}", u, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Load More", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # --- CREATIVE FOOTER ---
    # We use a CSS class 'footer-container' instead of <br> tags
    st.markdown(f"""
        <div class="footer-container">
            <p style="color: grey; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 10px;">PROUDLY DEVELOPED BY</p>
            <div class="footer-names">
                Buddhadeb • Arghadeep • Sanajit • Kamalakanta
            </div>
            <p style="color: grey; font-size: 0.7rem; margin-top: 20px;">© 2026 MoodTunes Music System</p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

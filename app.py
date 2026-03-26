import streamlit as st
import pandas as pd
import numpy as np

# --- THEME-AWARE AESTHETIC UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* 1. SEARCH BOX - Adapts to theme */
    .stTextInput input {
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(128, 128, 128, 0.3);
    }
    
    /* 2. MOOD BOX CONTAINER */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: nowrap !important;
        justify-content: space-between;
        gap: 12px;
        width: 100%;
        margin-top: 15px;
    }

    /* Hide standard radio UI */
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }

    /* 3. SLEEK MOOD BOXES */
    div[role="radiogroup"] label {
        flex: 1;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-weight: 700;
        font-size: 16px !important;
        color: white !important; /* Keep white for the colored gradients */
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        white-space: nowrap;
    }

    /* Vibrant Gradients (Work in both Light/Dark) */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(45deg, #FF512F, #DD2476); } /* All Songs */
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(45deg, #1A2980, #26D0CE); } /* Sad */
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(45deg, #FF0844, #FFB199); } /* Romantic */
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(45deg, #F09819, #EDDE5D); } /* Happy */

    /* Text Labels */
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }

    /* Selection State - White border in Dark, Dark border in Light */
    div[role="radiogroup"] [data-checked="true"] + div {
        border: 3px solid currentColor !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }

    /* 4. SONG CARD DESIGN */
    .song-card {
        padding: 15px;
        border-radius: 15px;
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 10px;
        transition: background 0.3s ease;
    }
    .song-card:hover {
        background: rgba(128, 128, 128, 0.1);
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
    st.title("🎵 MoodTunes")
    st.caption("Music Recommendation System")

with col_s:
    st.write("")
    search_query = st.text_input("Search", "", placeholder="🔍 Search songs or artists...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    
    st.write("### Choose Your Mood")
    mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

    # --- LOGIC ---
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
    if f_df.empty:
        st.warning("No matches found for your current search and mood.")
    else:
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        
        st.write(f"Showing **{show_now}** of **{len(recs)}** matches")
        
        for i in range(show_now):
            row = recs.iloc[i]
            # Custom Song Card Container
            st.markdown(f"""
                <div class="song-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold; font-size: 1.1rem;">{i+1}. {row['SongName']}</div>
                            <div style="opacity: 0.7; font-size: 0.9rem;">{row['ArtistName']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Button right below the card for better mobile/light use
            u = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
            st.link_button(f"▶️ Play {row['SongName']}", u, use_container_width=True)
            st.write("")

        if show_now < len(recs):
            if st.button("⬇️ Show More Songs", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # Footer
    st.markdown("<br><hr><p style='text-align: center; color: grey; font-size: 0.8rem; font-style: italic;'>Developed by: Buddhadeb, Arghadeep, Sanajit, & Kamalakanta</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Something went wrong while loading the music: {e}")

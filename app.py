import streamlit as st
import pandas as pd
import numpy as np

# --- FINAL PERMANENT UI ---
st.set_page_config(page_title="Music Recommendation System", layout="wide")

st.markdown("""
    <style>
    /* Search Box Styling */
    .stTextInput input { 
        border-radius: 8px; 
        border: 1px solid #444; 
        padding: 8px; 
    }
    
    /* Mood Box Container */
    div[role="radiogroup"] { 
        display: flex; 
        flex-wrap: nowrap !important; 
        justify-content: space-between; 
        gap: 10px; 
        width: 100%; 
        margin-top: 10px; 
    }
    
    /* Hide default radio elements */
    div[role="radiogroup"] > label > div [data-testid="stMarkdownContainer"] { display: none; }
    div[role="radiogroup"] [data-testid="stWidgetLabel"] { display: none; }
    div[role="radiogroup"] label p { display: none; }
    
    /* Sleek Mood Boxes */
    div[role="radiogroup"] label {
        flex: 1; height: 50px; display: flex; align-items: center; justify-content: center;
        border-radius: 10px; font-weight: 600; font-size: 14px !important; color: white !important;
        cursor: pointer; transition: all 0.2s ease; border: 2px solid transparent !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2); white-space: nowrap;
    }
    
    /* Gradients */
    div[role="radiogroup"] label:nth-of-type(1) { background: linear-gradient(135deg, #30cfd0, #330867); } 
    div[role="radiogroup"] label:nth-of-type(2) { background: linear-gradient(135deg, #1e3c72, #2a5298); } 
    div[role="radiogroup"] label:nth-of-type(3) { background: linear-gradient(135deg, #f093fb, #f5576c); } 
    div[role="radiogroup"] label:nth-of-type(4) { background: linear-gradient(135deg, #5ee7df, #b490ca); } 
    
    /* Text Labels */
    div[role="radiogroup"] label:nth-of-type(1)::after { content: "All Songs"; }
    div[role="radiogroup"] label:nth-of-type(2)::after { content: "Sad"; }
    div[role="radiogroup"] label:nth-of-type(3)::after { content: "Romantic"; }
    div[role="radiogroup"] label:nth-of-type(4)::after { content: "Happy"; }
    
    /* Selection State */
    div[role="radiogroup"] [data-checked="true"] + div { 
        border: 3px solid white !important; 
        box-shadow: 0 0 12px rgba(255,255,255,0.4); 
        transform: scale(1.02); 
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Looks for the file in the same folder on GitHub
    return pd.read_csv('SpotifySongs.csv')

# Pagination state
if 'display_count' not in st.session_state: 
    st.session_state.display_count = 20

# --- HEADER ---
col_t, col_s = st.columns([2.5, 1.5])
with col_t: 
    st.title("🎵 Music Recommendation System")

with col_s: 
    st.write("")
    # FIX: Added 'Search' placeholder so it's visible in the box
    search_query = st.text_input("Search", "", placeholder="Search for a song or artist...", label_visibility="collapsed")

try:
    df = load_data()
    mood_choices = ["All Songs", "Sad", "Romantic", "Happy/Energetic"]
    st.write("### Choose Mood")
    mood_choice = st.radio("Mood:", options=mood_choices, horizontal=True, label_visibility="collapsed")

    # --- LIVE RECOMMENDATION LOGIC ---
    # The app now filters automatically without needing a button click
    f_df = df.copy()
    
    # 1. Apply Search Filter
    if search_query.strip():
        q = search_query.strip().lower()
        f_df = f_df[f_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                    f_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

    # 2. Apply Mood Filter
    if mood_choice != "All Songs":
        if mood_choice == "Sad": 
            f_df = f_df[(f_df['Valence'] < 0.5) | (f_df['Acousticness'] > 0.6)]
        elif mood_choice == "Romantic": 
            f_df = f_df[(f_df['Valence'] > 0.25) & (f_df['Valence'] < 0.75) & (f_df['Energy'] < 0.7)]
        elif mood_choice == "Happy/Energetic": 
            f_df = f_df[(f_df['Valence'] > 0.55) | (f_df['Energy'] > 0.65)]

    # --- DISPLAY RESULTS ---
    st.write("") # Spacing
    if f_df.empty: 
        st.warning("No matches found. Try a different search or mood!")
    else:
        recs = f_df.reset_index(drop=True)
        show_now = min(st.session_state.display_count, len(recs))
        st.info(f"✅ Found **{len(recs)}** songs matching your criteria.")
        
        for i in range(show_now):
            row = recs.iloc[i]
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**{i+1}.** 🎶 **{row['SongName']}**")
                st.caption(f"Artist: {row['ArtistName']}")
            with c2:
                # Direct Spotify Search Link
                u = f"https://open.spotify.com/search/{row['SongName'].replace(' ', '%20')}%20{row['ArtistName'].replace(' ', '%20')}"
                st.link_button("▶️ Play", u)
            st.divider()

        # "Show More" functionality
        if show_now < len(recs):
            if st.button("⬇️ Show 20 More Songs", use_container_width=True):
                st.session_state.display_count += 20
                st.rerun()

    # Footer
    st.markdown("<br><hr><p style='text-align: center; color: grey; font-size: 0.8rem;'>Developed by: Buddhadeb, Arghadeep, Sanajit, & Kamalakanta</p>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")

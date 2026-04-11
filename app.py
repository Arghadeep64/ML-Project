import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
from pathlib import Path
from sklearn.cluster import KMeans

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'SpotifySongs.csv'

# --- 1. [TEAM MEMBER: KAMALAKANTA BERA] UI DESIGN & SYSTEM INTEGRATION ---
# Role: Integrator
# Responsibility: Designing the Streamlit UI and final system deployment.

st.set_page_config(page_title="MoodTunes Music System", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stAppToolbar"] {display: none !important;}

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

    h1, h2, h3, p, span, label, .stMetric div {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }

    /* FIX: Robust Search Input Styling */
    .stTextInput input,
    .stTextInput input:focus,
    .stTextInput input:-webkit-autofill {
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        padding: 12px !important;
        background-color: rgba(0, 0, 0, 0.35) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .stTextInput input::selection {
        background: rgba(29, 185, 84, 0.35) !important;
        color: #FFFFFF !important;
    }
    
    .stTextInput input:focus {
        border-color: #1DB954 !important;
        background-color: rgba(0, 0, 0, 0.45) !important;
        box-shadow: 0 0 0 1px #1DB954 !important;
    }

    .stTextInput input:-webkit-autofill {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stTextInput input::selection {
        background: rgba(29, 185, 84, 0.35) !important;
        color: #FFFFFF !important;
    }

    /* FIX: Show More Button Specific Styling */
    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        transition: 0.3s all ease !important;
        font-weight: bold !important;
    }

    div.stButton > button:hover {
        border-color: #1DB954 !important;
        color: #1DB954 !important;
        background-color: rgba(29, 185, 84, 0.1) !important;
    }

    /* Spotify Style Link Buttons */
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

    div[role="radiogroup"] { display: flex; flex-wrap: wrap !important; gap: 8px; margin-top: 10px; }
    div[role="radiogroup"] label {
        padding: 0px 15px; min-width: 110px; height: 48px; 
        display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-weight: 700; color: white !important; cursor: pointer; 
    }
    div[role="radiogroup"] [data-checked="true"] + div { 
        transform: scale(1.05); border: 2.5px solid white !important;
    }

    .song-card {
        padding: 25px; border-radius: 20px;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
        transition: 0.3s ease;
    }
    .song-card:hover { border-color: #1DB954; }

    .footer-container {
        margin-top: 100px; padding: 50px; text-align: center;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. [TEAM MEMBER: BUDDHADEB PAN] DATA COLLECTION & PREPARATION ---
# Role: Data Collector
# Responsibility: Gathering the Spotify dataset (CSV) and preparing it for modeling.

@st.cache_data
def load_and_prepare_dataset():
    if DATA_PATH.exists():
        data = pd.read_csv(DATA_PATH)
        return data.dropna()
    return pd.DataFrame()

@st.cache_data
def cluster_songs_and_assign_moods(df):
    if df.empty:
        return df, {}
    
    # Features for clustering
    features = ['Popularity', 'Danceability', 'Energy', 'Loudness', 'Speechiness', 
                'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Duration_ms']
    
    # Standardize features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])
    
    # K-Means clustering into 8 clusters (for 8 moods)
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    df = df.copy()
    df['cluster'] = kmeans.fit_predict(scaled_features)
    
    # Assign moods based on cluster centroids with a unique mapping
    centroids = kmeans.cluster_centers_
    mood_labels = ["Sad", "Romantic", "Workout", "Focus", "Chill", "Dance", "Party"]
    cluster_moods = {}
    assigned_clusters = set()

    def mood_score(cluster_features, mood):
        valence = cluster_features['Valence']
        energy = cluster_features['Energy']
        danceability = cluster_features['Danceability']
        acousticness = cluster_features['Acousticness']
        instrumentalness = cluster_features['Instrumentalness']
        loudness = cluster_features['Loudness']

        if mood == "Sad":
            return -valence * 1.0 + -energy * 0.9 + -loudness * 0.4
        if mood == "Romantic":
            return valence * 1.0 + -energy * 0.6 + -loudness * 0.4 + (0.4 - danceability)
        if mood == "Workout":
            return energy * 1.1 + loudness * 0.7 + danceability * 0.5
        if mood == "Focus":
            return acousticness * 0.9 + instrumentalness * 1.0 - energy * 0.3
        if mood == "Chill":
            return -energy * 0.9 + -loudness * 0.7 + acousticness * 0.3
        if mood == "Dance":
            return danceability * 1.2 + energy * 0.5
        if mood == "Party":
            return danceability * 0.9 + energy * 0.9 + valence * 0.7
        return 0.0

    cluster_features = []
    for i in range(8):
        centroid = centroids[i]
        cluster_features.append({
            'cluster': i,
            'Valence': centroid[features.index('Valence')],
            'Energy': centroid[features.index('Energy')],
            'Danceability': centroid[features.index('Danceability')],
            'Acousticness': centroid[features.index('Acousticness')],
            'Instrumentalness': centroid[features.index('Instrumentalness')],
            'Loudness': centroid[features.index('Loudness')],
        })

    for mood in mood_labels:
        best_cluster = None
        best_score = None
        for cluster in cluster_features:
            if cluster['cluster'] in assigned_clusters:
                continue
            score = mood_score(cluster, mood)
            if best_cluster is None or score > best_score:
                best_cluster = cluster['cluster']
                best_score = score
        if best_cluster is not None:
            cluster_moods[best_cluster] = mood
            assigned_clusters.add(best_cluster)

    # Assign any remaining cluster to Chill as a fallback
    for cluster in range(8):
        if cluster not in assigned_clusters:
            cluster_moods[cluster] = "Chill"

    return df, cluster_moods

# --- 3. [TEAM MEMBER: ARGHADEEP GHOSH] RECOMMENDATION MODEL BUILDER ---
# Role: ML Builder
# Responsibility: Building the similarity logic and mood-based algorithms.

def get_mood_recommendations(df, mood, cluster_moods):
    if mood == "All Songs":
        return df

    cluster_ids = [cid for cid, m in cluster_moods.items() if m == mood]
    if cluster_ids:
        return df[df['cluster'].isin(cluster_ids)]
    return df

# --- 4. [TEAM MEMBER: SANAJIT SAHOO] TESTING & EVALUATION ---
# Role: Tester
# Responsibility: Verifying accuracy and checking recommendation quality.

if 'display_limit' not in st.session_state: 
    st.session_state.display_limit = 20

st.title("🎵 Music Recommendation System")
st.markdown("<p style='opacity: 0.7; font-size: 1.1rem; font-weight: 300; margin-top: -15px;'>Your mood deserves the perfect soundtrack.</p>", unsafe_allow_html=True)

try:
    df = load_and_prepare_dataset()
    if df.empty:
        st.error("⚠️ Dataset not found. Please upload 'SpotifySongs.csv'.")
    else:
        df, cluster_moods = cluster_songs_and_assign_moods(df)
        
        # Search & Interaction
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...", label_visibility="collapsed")
        
        st.write("### ✨ Match your Mood")
        mood_choices = ["All Songs", "Sad", "Romantic", "Workout", "Focus", "Chill", "Dance", "Party"]
        
        # UI Styling for Mood Buttons
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
        
        mood_choice = st.radio("Mood Selector", options=mood_choices, index=0, horizontal=True, label_visibility="collapsed")

        # ML Recommendation Logic
        filtered_df = get_mood_recommendations(df, mood_choice, cluster_moods)
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[filtered_df['SongName'].astype(str).str.lower().str.contains(q, na=False) | 
                                    filtered_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        # Evaluation Statistics
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

        # Final Branding & Presentation Footer
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

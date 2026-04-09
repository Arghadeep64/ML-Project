import streamlit as st
import pandas as pd
import numpy as np
import os
import urllib.parse
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score

# --- 1. UI DESIGN ---
st.set_page_config(page_title="MoodTunes Music System", layout="wide")

# --- 2. DATA COLLECTION ---
@st.cache_data
def load_and_prepare_dataset():
    if os.path.exists('SpotifySongs.csv'):
        data = pd.read_csv('SpotifySongs.csv')
        return data.dropna()
    return pd.DataFrame()

# --- 3. RULE-BASED RECOMMENDATION ---
def get_mood_recommendations(df, mood):
    if mood == "Sad": return df[df['Valence'] < 0.4]
    elif mood == "Romantic": return df[(df['Valence'] > 0.4) & (df['Valence'] < 0.6) & (df['Energy'] < 0.6)]
    elif mood == "Workout": return df[(df['Energy'] > 0.7) & (df['Tempo'] > 115)]
    elif mood == "Party": return df[(df['Danceability'] > 0.7) & (df['Energy'] > 0.7)]
    elif mood == "Focus": return df[(df['Instrumentalness'] > 0.4) | (df['Energy'] < 0.5)]
    elif mood == "Chill": return df[(df['Energy'] < 0.4) & (df['Loudness'] < -10)]
    elif mood == "Dance": return df[df['Danceability'] > 0.8]
    return df

# --- 4. RANDOM FOREST TRAINING ---
def train_random_forest(df):
    # Create artificial mood labels based on rule-based logic
    conditions = [
        (df['Valence'] < 0.4),  # Sad
        ((df['Valence'] > 0.4) & (df['Valence'] < 0.6) & (df['Energy'] < 0.6)),  # Romantic
        ((df['Energy'] > 0.7) & (df['Tempo'] > 115)),  # Workout
        ((df['Danceability'] > 0.7) & (df['Energy'] > 0.7)),  # Party
        ((df['Instrumentalness'] > 0.4) | (df['Energy'] < 0.5)),  # Focus
        ((df['Energy'] < 0.4) & (df['Loudness'] < -10)),  # Chill
        (df['Danceability'] > 0.8)  # Dance
    ]
    labels = ['Sad','Romantic','Workout','Party','Focus','Chill','Dance']
    df['MoodLabel'] = np.select(conditions, labels, default='Other')

    features = ['Valence','Energy','Danceability','Tempo','Loudness','Instrumentalness']
    X = df[features]
    y = df['MoodLabel']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Cross-validation score
    cv_score = cross_val_score(rf, X, y, cv=5).mean()
    return rf, cv_score

# --- 5. K-MEANS CLUSTERING ---
def apply_kmeans(df, n_clusters=6):
    features = ['Valence','Energy','Danceability','Tempo','Loudness','Instrumentalness']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    return df, kmeans

# --- 6. STREAMLIT APP ---
if 'display_limit' not in st.session_state:
    st.session_state.display_limit = 20

st.title("🎵 Music Recommendation System")

try:
    df = load_and_prepare_dataset()
    if df.empty:
        st.error("⚠️ Dataset not found. Please upload 'SpotifySongs.csv'.")
    else:
        # Train Random Forest
        rf_model, rf_score = train_random_forest(df)
        st.metric("Random Forest CV Accuracy", f"{rf_score:.2f}")

        # Apply KMeans
        df, kmeans_model = apply_kmeans(df, n_clusters=6)

        # Search & Mood Selection
        search_query = st.text_input("Search", "", placeholder="🔍 Search track or artist...")
        mode_choice = st.radio("Recommendation Mode", ["Rule-Based", "Random Forest Prediction", "K-Means Clusters"], horizontal=True)

        if mode_choice == "Rule-Based":
            mood_choices = ["All Songs","Sad","Romantic","Workout","Party","Focus","Chill","Dance"]
            mood_choice = st.radio("Mood Selector", options=mood_choices, horizontal=True)
            filtered_df = get_mood_recommendations(df, mood_choice)

        elif mode_choice == "Random Forest Prediction":
            # Predict moods for all songs
            features = ['Valence','Energy','Danceability','Tempo','Loudness','Instrumentalness']
            df['PredictedMood'] = rf_model.predict(df[features])
            mood_choices = df['PredictedMood'].unique().tolist()
            mood_choice = st.radio("Predicted Mood Selector", options=mood_choices, horizontal=True)
            filtered_df = df[df['PredictedMood'] == mood_choice]

        else:  # K-Means
            cluster_choices = sorted(df['Cluster'].unique())
            cluster_choice = st.radio("Cluster Selector", options=cluster_choices, horizontal=True)
            filtered_df = df[df['Cluster'] == cluster_choice]

        # Search filter
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_df = filtered_df[filtered_df['SongName'].astype(str).str.lower().str.contains(q, na=False) |
                                      filtered_df['ArtistName'].astype(str).str.lower().str.contains(q, na=False)]

        st.metric("Songs Found", len(filtered_df))
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

except Exception as e:
    st.error(f"System Error: {e}")

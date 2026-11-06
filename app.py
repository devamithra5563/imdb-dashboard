import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="IMDb Top 250 Movie Analytics",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #F5C518; }
    .stButton>button { background-color: #F5C518; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = "ToP 250 movies on imdb in 2026.csv"
    try:
        df = pd.read_csv(file_path)
    except Exception:
        import glob
        files = glob.glob("*imdb*.csv") + glob.glob("*IMDb*.csv") + glob.glob("*.csv")
        if files:
            df = pd.read_csv(files[0])
        else:
            st.error("Could not find dataset CSV file.")
            return pd.DataFrame()
    
    if 'averageRating' in df.columns:
        df['averageRating'] = pd.to_numeric(df['averageRating'], errors='coerce')
    if 'numVotes' in df.columns:
        df['numVotes'] = pd.to_numeric(df['numVotes'], errors='coerce')
    if 'grossWorldwide' in df.columns:
        df['grossWorldwide'] = pd.to_numeric(df['grossWorldwide'], errors='coerce')
        
    return df

df = load_data()

st.markdown('<p class="main-title">🎬 IMDb Top 250 Movie Analytics Dashboard</p>', unsafe_allow_html=True)
st.write("An interactive analytics dashboard built with Python & Streamlit.")
st.markdown("---")

if df.empty:
    st.warning("Please ensure 'ToP 250 movies on imdb in 2026.csv' is present in your project directory.")
    st.stop()

st.sidebar.header("🔍 Filter Options")
search_query = st.sidebar.text_input("Search Movie Title", "")

min_rating = float(df['averageRating'].min()) if 'averageRating' in df.columns else 0.0
max_rating = float(df['averageRating'].max()) if 'averageRating' in df.columns else 10.0

rating_range = st.sidebar.slider(
    "Select IMDb Rating Range",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating),
    step=0.1
)

if 'genres' in df.columns:
    genres_set = set()
    for g in df['genres'].dropna():
        for genre in str(g).split(','):
            genres_set.add(genre.strip())
    sorted_genres = sorted(list(genres_set))
    selected_genres = st.sidebar.multiselect("Select Genre(s)", options=sorted_genres, default=[])
else:
    selected_genres = []

filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[filtered_df['primaryTitle'].astype(str).str.contains(search_query, case=False, na=False)]

if 'averageRating' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['averageRating'] >= rating_range[0]) & 
        (filtered_df['averageRating'] <= rating_range[1])
    ]

if selected_genres and 'genres' in filtered_df.columns:
    pattern = '|'.join(selected_genres)
    filtered_df = filtered_df[filtered_df['genres'].astype(str).str.contains(pattern, case=False, na=False)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Movies Shown", len(filtered_df))
if 'averageRating' in filtered_df.columns and not filtered_df.empty:
    col2.metric("Avg IMDb Rating", round(filtered_df['averageRating'].mean(), 2))
if 'numVotes' in filtered_df.columns and not filtered_df.empty:
    col3.metric("Avg Votes", f"{int(filtered_df['numVotes'].mean()):,}")
if 'grossWorldwide' in filtered_df.columns and not filtered_df.empty:
    col4.metric("Avg Gross Worldwide", f"${filtered_df['grossWorldwide'].mean():,.0f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Analytics & Visualizations", "📋 Data Table", "🔎 Movie Search & Details"])

with tab1:
    st.subheader("Data Visualizations")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Top 10 Highest Rated Movies")
        if 'primaryTitle' in filtered_df.columns and 'averageRating' in filtered_df.columns:
            top10_rating = filtered_df.sort_values(by='averageRating', ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=top10_rating, x='averageRating', y='primaryTitle', palette='viridis', ax=ax)
            ax.set_xlabel("IMDb Rating")
            ax.set_ylabel("Movie Title")
            st.pyplot(fig)

    with c2:
        st.markdown("#### Rating Distribution")
        if 'averageRating' in filtered_df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.histplot(filtered_df['averageRating'], bins=15, kde=True, color='#F5C518', ax=ax)
            ax.set_xlabel("IMDb Rating")
            ax.set_ylabel("Count")
            st.pyplot(fig)

    st.markdown("---")
    
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Rating vs. Total Votes")
        if 'averageRating' in filtered_df.columns and 'numVotes' in filtered_df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.scatterplot(data=filtered_df, x='numVotes', y='averageRating', color='crimson', alpha=0.7, ax=ax)
            ax.set_xlabel("Total Votes")
            ax.set_ylabel("IMDb Rating")
            st.pyplot(fig)
            
    with c4:
        st.markdown("#### Genre Frequency")
        if 'genres' in filtered_df.columns and not filtered_df.empty:
            all_g = []
            for item in filtered_df['genres'].dropna():
                all_g.extend([g.strip() for g in str(item).split(',')])
            genre_counts = pd.Series(all_g).value_counts().head(8)
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x=genre_counts.values, y=genre_counts.index, palette='magma', ax=ax)
            ax.set_xlabel("Number of Movies")
            ax.set_ylabel("Genre")
            st.pyplot(fig)

with tab2:
    st.subheader("Filtered Dataset View")
    st.write(f"Showing {len(filtered_df)} of {len(df)} records")
    st.dataframe(filtered_df, use_container_width=True)

with tab3:
    st.subheader("Detailed Search")
    selected_movie = st.selectbox("Select a Movie to View Details:", filtered_df['primaryTitle'].unique() if not filtered_df.empty else [])
    if selected_movie:
        movie_data = df[df['primaryTitle'] == selected_movie].iloc[0]
        st.json(movie_data.to_dict())

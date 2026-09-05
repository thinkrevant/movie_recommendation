import streamlit as st
import pickle
import requests

st.set_page_config(page_title="Movie Recommender", layout="wide", page_icon="🎬")

st.markdown("""
<style>
    .main { padding: 2rem; }
    .title {
        font-size: 48px;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #e50914, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 16px;
        margin-bottom: 2rem;
    }
    .movie-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: transform 0.2s;
        border: 1px solid #333;
    }
    .movie-title {
        font-size: 13px;
        font-weight: 600;
        color: #ffffff;
        margin-top: 8px;
        line-height: 1.3;
    }
    .rating {
        font-size: 12px;
        color: #f5c518;
        margin-top: 4px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #e50914, #ff6b6b);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 40px;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }
    .stSelectbox > div {
        border-radius: 10px;
    }
    div[data-testid="stImage"] img {
        border-radius: 10px;
        width: 100%;
    }
    .section-header {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        margin: 2rem 0 1rem;
        border-left: 4px solid #e50914;
        padding-left: 12px;
    }
</style>
""", unsafe_allow_html=True)

movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=b6fd929151492d94b4252b675a93fbe4&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path', None)
        rating = round(data.get('vote_average', 0), 1)
        if poster_path and poster_path != 'None':
            poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster = "https://via.placeholder.com/500x750?text=No+Poster"
        return poster, rating
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=No+Poster", "N/A"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),
                      reverse=True, key=lambda x: x[1])[1:6]
    names, posters, ratings = [], [], []
    for i in distances:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        poster, rating = fetch_movie_details(movie_id)
        posters.append(poster)
        ratings.append(rating)
    return names, posters, ratings

# ── Header ────────────────────────────────────────────────
st.markdown('<div class="title">🎬 CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find your next favourite movie instantly</div>', unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────
col_left, col_mid, col_right = st.columns([1, 3, 1])
with col_mid:
    selected_movie = st.selectbox(
        'Search for a movie',
        movies['title'].values,
        label_visibility='collapsed',
        placeholder='Type a movie name...'
    )
    recommend_btn = st.button('🎯 Get Recommendations')

# ── Results ───────────────────────────────────────────────
if recommend_btn:
    with st.spinner('Finding the best matches for you...'):
        names, posters, ratings = recommend(selected_movie)

    st.markdown(f'<div class="section-header">Because you liked {selected_movie}</div>',
                unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    for col, name, poster, rating in zip(cols, names, posters, ratings):
        with col:
            st.image(poster, use_container_width=True)
            st.markdown(f'<div class="movie-title">{name}</div>',
                       unsafe_allow_html=True)
            st.markdown(f'<div class="rating">⭐ {rating}</div>',
                       unsafe_allow_html=True)
# ── Footer ────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#555; font-size:13px;">Built with Python · Scikit-learn · Streamlit · TMDB API</p>',
    unsafe_allow_html=True
)
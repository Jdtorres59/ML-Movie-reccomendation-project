import os
from pathlib import Path

import difflib
import pandas as pd
import requests
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

APP_TITLE = os.getenv("APP_TITLE", "CineScope")
APP_TAGLINE = os.getenv("APP_TAGLINE", "Find your next favorite movie")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

DATA_PATH = Path(__file__).with_name("movies.csv")

MOVIES_DATA = pd.read_csv(DATA_PATH)

SELECTED_FEATURES = ["keywords", "genres", "tagline", "cast", "director"]
for feature in SELECTED_FEATURES:
    MOVIES_DATA[feature] = MOVIES_DATA[feature].fillna("")

COMBINED_FEATURES = (
    MOVIES_DATA["genres"]
    + " "
    + MOVIES_DATA["keywords"]
    + " "
    + MOVIES_DATA["tagline"]
    + " "
    + MOVIES_DATA["cast"]
    + " "
    + MOVIES_DATA["director"]
)

VECTORIZER = TfidfVectorizer()
FEATURE_VECTORS = VECTORIZER.fit_transform(COMBINED_FEATURES)
SIMILARITY = cosine_similarity(FEATURE_VECTORS)

ALL_TITLES = MOVIES_DATA["title"].fillna("").tolist()

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
POSTER_CACHE = {}
SESSION = requests.Session()

app = Flask(__name__)


def _normalize_text(value: str) -> str:
    return value.strip()


def _resolve_title(query: str):
    cleaned = _normalize_text(query)
    if not cleaned:
        return None, "empty"

    exact_match = next(
        (title for title in ALL_TITLES if title.lower() == cleaned.lower()),
        None,
    )
    if exact_match:
        return exact_match, None

    matches = difflib.get_close_matches(cleaned, ALL_TITLES, n=1, cutoff=0.6)
    if not matches:
        return None, "not_found"

    return matches[0], None


def _get_year(release_date):
    if isinstance(release_date, str) and len(release_date) >= 4:
        return release_date[:4]
    return "-"


def _format_rating(value):
    if pd.isna(value):
        return "-"
    return f"{value:.1f}"


def _format_similarity(score):
    if score is None:
        return ""
    return f"{score:.0%}"


def _fetch_poster(title: str):
    cache_key = title.lower().strip()
    if cache_key in POSTER_CACHE:
        return POSTER_CACHE[cache_key]

    if not TMDB_API_KEY:
        POSTER_CACHE[cache_key] = None
        return None

    try:
        response = SESSION.get(
            TMDB_SEARCH_URL,
            params={"api_key": TMDB_API_KEY, "query": title},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        poster_path = results[0].get("poster_path") if results else None
        poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
        POSTER_CACHE[cache_key] = poster_url
        return poster_url
    except requests.RequestException:
        POSTER_CACHE[cache_key] = None
        return None


def _get_index_for_title(title: str):
    if "index" in MOVIES_DATA.columns:
        return MOVIES_DATA[MOVIES_DATA.title == title]["index"].values[0]
    return MOVIES_DATA[MOVIES_DATA.title == title].index[0]


def get_recommendations(title: str, limit: int = 12):
    index_of_movie = _get_index_for_title(title)
    similarity_scores = list(enumerate(SIMILARITY[index_of_movie]))
    sorted_similar_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for index, score in sorted_similar_movies:
        if index == index_of_movie:
            continue
        row = MOVIES_DATA.iloc[index]
        recommendations.append(
            {
                "title": row.get("title", ""),
                "year": _get_year(row.get("release_date", "")),
                "rating": _format_rating(row.get("vote_average")),
                "overview": row.get("overview")
                if isinstance(row.get("overview"), str) and row.get("overview")
                else "No overview available.",
                "genres": row.get("genres", ""),
                "cast": row.get("cast", ""),
                "director": row.get("director", ""),
                "tagline": row.get("tagline", ""),
                "similarity": score,
                "similarity_label": _format_similarity(score),
                "poster_url": _fetch_poster(row.get("title", "")),
            }
        )
        if len(recommendations) >= limit:
            break

    return recommendations


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        app_title=APP_TITLE,
        app_tagline=APP_TAGLINE,
        titles=ALL_TITLES,
        recommendations=None,
        query="",
        resolved_title=None,
        error=None,
        tmdb_ready=bool(TMDB_API_KEY),
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    query = request.form.get("movie", "")
    resolved_title, error = _resolve_title(query)

    error_message = None
    if error == "empty":
        error_message = "Type a movie title to get recommendations."
    elif error == "not_found":
        error_message = "We could not find a close match. Try another title."

    recommendations = None
    if not error:
        recommendations = get_recommendations(resolved_title)

    return render_template(
        "index.html",
        app_title=APP_TITLE,
        app_tagline=APP_TAGLINE,
        titles=ALL_TITLES,
        recommendations=recommendations,
        query=query,
        resolved_title=resolved_title,
        error=error_message,
        tmdb_ready=bool(TMDB_API_KEY),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

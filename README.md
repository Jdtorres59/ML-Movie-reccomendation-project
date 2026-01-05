# CineScope - Movie Recommender

CineScope is a Netflix-inspired, content-based movie recommender built on TF-IDF and cosine similarity. Search a movie you love and explore curated recommendations with posters, ratings, and details. It is designed as a polished portfolio demo that is simple to deploy.

## Why I built it
I wanted a clean, production-style showcase of classic ML recommendation logic with a premium UI. The goal is to merge solid data science foundations with a product-ready experience.

## Key Features
- Content-based recommendations using TF-IDF + cosine similarity
- Netflix-inspired UI with responsive poster grid and modal details
- Autocomplete suggestions and typo-friendly search
- TMDB poster fetching with in-memory caching
- Graceful empty, error, and loading states

## Tech Stack
- Flask, Jinja, Python
- Pandas, scikit-learn
- TMDB API for posters

## How it works
The app precomputes TF-IDF vectors from keywords, genres, tagline, cast, and director. Cosine similarity ranks related titles, and results are enriched with metadata and TMDB posters.

## Local setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export TMDB_API_KEY="your_key"
python app.py
```

## Deploy on Render
Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
gunicorn app:app
```

Environment variables:
- TMDB_API_KEY
- APP_TITLE (optional)
- APP_TAGLINE (optional)

## Demo
Demo: https://cinescopeml.onrender.com/
Repo: https://github.com/Jdtorres59/ML-Movie-reccomendation-project.git
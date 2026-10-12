# ARTBATTLE

Premium competitive art web application built with Django.

## Included
- Registration / login / logout
- Artist profiles and portfolio
- Weekly battles
- Artwork uploads
- One-entry-per-artist-per-battle rule
- Public voting with one vote per user per artwork
- Self-vote prevention
- Global leaderboard
- Winner history
- Monthly championship area
- Django admin management
- Basic artwork integrity layer: SHA-256 exact-duplicate detection + AI declaration
- Responsive premium UI
- SQLite database for easy local setup

## Run on Windows

```bat
cd ARTBATTLE
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Open http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

## Important
The integrity layer is intentionally honest: it detects exact duplicate image files and records an artist's AI declaration. It is NOT a claim of reliable AI-image detection. A production deployment should add a dedicated moderation/detection service and stronger anti-fraud controls.

For production, change SECRET_KEY, DEBUG, ALLOWED_HOSTS, storage, database, HTTPS/security settings, email, rate limiting, and media validation.

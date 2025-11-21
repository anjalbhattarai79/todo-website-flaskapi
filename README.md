# Flask TODO App 📝

Simple TODO web app using Flask and SQLAlchemy. Uses SQLite by default and can connect to PostgreSQL when a `DATABASE_URL` environment variable is provided.

## Technology used 🔧
- Python 🐍
- Flask ⚗️
- Flask-SQLAlchemy 🗄️
- SQLite (default) 🗂️
- PostgreSQL (optional, via `DATABASE_URL`) 🐘

## What I learned 🧠
- Basic Flask app structure (routes, templates) 🔁
- Defining models with SQLAlchemy and performing CRUD 🛠️
- Handling deployment DB URLs (adjusting `postgres://` → `postgresql://` and removing query params) 🔍
- Creating tables at startup with `db.create_all()` ✅
- Simple form handling and redirects ↩️


## Notes ℹ️
- By default the app uses `sqlite:///todo.db` when `DATABASE_URL` is not set.
- The app binds to port from `PORT` env var or 8000 by default.
- To persist production-grade data on PostgreSQL, supply a proper `DATABASE_URL` 🏷️

## Minimal file overview 📁
- app.py — main Flask application and SQLAlchemy model(s)
- templates/ — HTML templates used by `render_template` (index.html, update.html)

That's it — you can now add, update, and delete TODO items locally. 🎉

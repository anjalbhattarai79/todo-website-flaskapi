from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------------
# DATABASE CONFIG (FIXED)
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Critical fix #1: Azure still gives postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Critical fix #2: Azure adds ?sslmode=require at the end → SQLAlchemy hates that in the URI for Postgres
    # This safely removes query parameters that break SQLAlchemy on some platforms
    if "azure.com" in DATABASE_URL or "neon.tech" in DATABASE_URL or "supabase.co" in DATABASE_URL:
        # Keep only the main part, add sslmode as a connect_arg instead (see below)
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        DATABASE_URL = urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            '', '', ''  # remove params and query
        ))

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

    # This is the real magic for Azure + Neon + Supabase + Vercel
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"sslmode": "require"} if DATABASE_URL and DATABASE_URL.startswith("postgresql") else {}
    }
else:
    # Local dev
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -----------------------------
# MODEL (unchanged, perfect)
# -----------------------------
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"


# -----------------------------
# ROUTES (perfect)
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("hello_world"))

    allTodo = Todo.query.all()
    return render_template("index.html", allTodo=allTodo)


@app.route("/show")
def products():
    allTodo = Todo.query.all()
    print(allTodo)
    return "<p>This is product page</p>"


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    if request.method == "POST":
        todo.title = request.form["title"]
        todo.desc = request.form["desc"]
        db.session.commit()
        return redirect(url_for("hello_world"))
    return render_template("update.html", todo=todo)


@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    with app.app_context():
        db.create_all()  # This works perfectly on first deploy

    app.run(host="0.0.0.0", port=port, debug=False)
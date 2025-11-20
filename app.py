import os; os.chdir(os.path.dirname(__file__))
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import urllib.parse

app = Flask(__name__)

# -----------------------------
# DATABASE CONFIG – WORKS ON AZURE + VERCEL + EVERYWHERE
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    url = DATABASE_URL.strip()
    print(f"Found DATABASE_URL: {url[:60]}...")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Remove ?sslmode=require and everything after it
    if "?" in url:
        url = url.split("?")[0]

    app.config["SQLALCHEMY_DATABASE_URI"] = url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"sslmode": "require"}
    }
    print("Connected to Neon PostgreSQL!")
else:
    print("No DATABASE_URL → using local SQLite")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -----------------------------
# MODEL
# -----------------------------
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# -----------------------------
# CREATE TABLES – THIS RUNS ON AZURE TOO!
# -----------------------------
with app.app_context():
    db.create_all()
    print("Database tables ready")

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()
    return render_template("index.html", allTodo=allTodo)

@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    if request.method == "POST":
        todo.title = request.form["title"]
        todo.desc = request.form["desc"]
        db.session.commit()
        return redirect("/")
    return render_template("update.html", todo=todo)

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

# -----------------------------
# ONLY FOR LOCAL RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/uploads"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    if user:
        session["user"] = dict(user)
        flash("Login realizado com sucesso.", "success")
        return redirect(url_for("dashboard"))
    flash("Credenciais inválidas.", "danger")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sessão encerrada.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("index"))
    return render_template("dashboard.html")

@app.route("/users", methods=["GET", "POST"])
def users():
    db = get_db()
    if request.method == "POST":
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (request.form["username"], request.form["password"], request.form["role"]))
        db.commit()
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html", users=users)

@app.route("/users/delete/<int:user_id>")
def delete_user(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    return redirect(url_for("users"))

@app.route("/departments", methods=["GET", "POST"])
def departments():
    db = get_db()
    if request.method == "POST":
        db.execute("INSERT INTO departments (name, description) VALUES (?, ?)",
                   (request.form["name"], request.form["description"]))
        db.commit()
    departments = db.execute("SELECT * FROM departments").fetchall()
    return render_template("departments.html", departments=departments)

@app.route("/departments/delete/<int:dept_id>")
def delete_department(dept_id):
    db = get_db()
    db.execute("DELETE FROM departments WHERE id=?", (dept_id,))
    db.commit()
    return redirect(url_for("departments"))

@app.route("/schedules", methods=["GET", "POST"])
def schedules():
    db = get_db()
    if request.method == "POST":
        file = request.files["file"]
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        db.execute("INSERT INTO schedules (title, filename, date, department_id, uploaded_by) VALUES (?, ?, ?, ?, ?)",
                   (request.form["title"], filename, request.form["date"], request.form["department_id"], session["user"]["username"]))
        db.commit()
    schedules = db.execute("SELECT * FROM schedules ORDER BY date DESC").fetchall()
    return render_template("schedules.html", schedules=schedules)

@app.route("/mana", methods=["GET", "POST"])
def mana():
    db = get_db()
    if request.method == "POST":
        from datetime import date
        db.execute("INSERT INTO mana (date, content) VALUES (?, ?)",
                   (date.today().isoformat(), request.form["content"]))
        db.commit()
    mana = db.execute("SELECT * FROM mana ORDER BY date DESC").fetchall()
    return render_template("mana.html", mana=mana)

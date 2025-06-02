
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Conexão com banco de dados
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabelas
def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            filename TEXT,
            department TEXT,
            uploaded_by TEXT
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            is_read INTEGER DEFAULT 0
        )""")
init_db()

@app.route('/')
def index():
    db = get_db()
    schedules = db.execute("SELECT * FROM schedules ORDER BY id DESC").fetchall()
    return render_template('index.html', schedules=schedules)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    if user:
        session['user'] = dict(user)
        flash('Login realizado com sucesso.', 'success')
    else:
        flash('Credenciais inválidas.', 'danger')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout realizado.', 'info')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        flash('Faça login primeiro.', 'warning')
        return redirect(url_for('index'))

    file = request.files['file']
    title = request.form['title']
    department = request.form['department']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        db = get_db()
        db.execute("INSERT INTO schedules (title, filename, department, uploaded_by) VALUES (?, ?, ?, ?)",
                   (title, filename, department, session['user']['username']))
        db.commit()
        flash('Escala enviada com sucesso.', 'success')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

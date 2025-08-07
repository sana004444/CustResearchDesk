from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # User table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    # Submission table
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        abstract TEXT,
        authors TEXT,
        emails TEXT,
        corresponding_author TEXT,
        topics TEXT,
        agreement INTEGER,
        paper_filename TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)", 
                      (name, email, password, role))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Email already registered"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = {'id': user[0], 'name': user[1], 'role': user[4]}
            if user[4] == 'Author':
                return redirect('/dashboard/author')
            elif user[4] == 'Reviewer':
                return redirect('/dashboard/reviewer')
            elif user[4] == 'Chair':
                return redirect('/dashboard/chair')
        return "Invalid credentials"
    return render_template('login.html')

# Author Dashboard - View & Submit
@app.route('/dashboard/author', methods=['GET', 'POST'])
def author_dashboard():
    user = session.get('user')
    if not user or user['role'] != 'Author':
        return redirect('/login')

    user_id = user['id']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        authors = request.form['authors']
        emails = request.form['emails']
        corresponding_author = request.form['corresponding_author']
        topics = ', '.join(request.form.getlist('topics'))
        agreement = 1 if 'agreement' in request.form else 0
        file = request.files['paper_pdf']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Check if a submission exists for this user
            c.execute("SELECT * FROM submissions WHERE user_id = ?", (user_id,))
            existing = c.fetchone()

            if existing:
                # Update existing submission
                c.execute('''UPDATE submissions SET
                            title=?, abstract=?, authors=?, emails=?,
                            corresponding_author=?, topics=?, agreement=?, paper_filename=?
                            WHERE user_id=?''',
                          (title, abstract, authors, emails, corresponding_author,
                           topics, agreement, filename, user_id))
            else:
                # New submission
                c.execute('''INSERT INTO submissions
                            (user_id, title, abstract, authors, emails, corresponding_author,
                             topics, agreement, paper_filename)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, title, abstract, authors, emails, corresponding_author,
                           topics, agreement, filename))

            conn.commit()
            flash("Paper submitted successfully!")

    # Fetch existing submission (for view/edit)
    c.execute("SELECT * FROM submissions WHERE user_id = ?", (user_id,))
    submission = c.fetchone()
    conn.close()

    return render_template('dashboard/author_dashboard.html', user=user, submission=submission)

@app.route('/dashboard/reviewer')
def reviewer_dashboard():
    return render_template('dashboard/reviewer_dashboard.html', user=session.get('user'))

@app.route('/dashboard/chair')
def chair_dashboard():
    return render_template('dashboard/chair_dashboard.html', user=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True)

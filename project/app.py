#Main Flask app, routes and logic for the web application
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Path to users.json file
USERS_FILE = os.path.join(os.path.dirname(__file__), '../Data/users.json')

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}


def load_user(username):
    users = load_users()
    user = users.get(username)
    if user is None:
        return None
    if isinstance(user, str):
        return {
            'password': user,
            'trips': []
        }
    if isinstance(user, dict):
        user.setdefault('trips', [])
        return user
    return {
        'password': '',
        'trips': []
    }


def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def username_exists(username):
    """Check if username already exists"""
    users = load_users()
    return username in users

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validate inputs
        if not username or not password:
            return render_template('login.html', error='Username and password are required')

        # Load user record
        user = load_user(username)
        if not user:
            return render_template('login.html', error='Username not found. Please sign up first.')

        # Verify password (check hashed password)
        if not check_password_hash(user['password'], password):
            return render_template('login.html', error='Incorrect password. Please try again.')

        session['username'] = username
        return redirect(url_for('profile'))

    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirmPassword', '').strip()

        # Validate inputs
        if not username or not password or not confirm_password:
            return render_template('signup.html', error='Username and passwords are required')

        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        if username_exists(username):
            return render_template('signup.html', error='Username already exists. Please choose a different username.')

        users = load_users()
        users[username] = {
            'password': generate_password_hash(password),
            'trips': []
        }
        save_users(users)

        session['username'] = username
        return redirect(url_for('profile'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    user = load_user(username)
    saved_trips = user.get('trips', []) if user else []
    return render_template('profile.html', username=username, saved_trips=saved_trips)



if __name__ == '__main__':
    app.run(debug=True)
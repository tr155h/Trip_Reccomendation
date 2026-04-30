#Main Flask app, routes and logic for the web application
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Path to users.json file
USERS_FILE = os.path.join(os.path.dirname(__file__), '../Data/users.json')

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                return json.load(open(USERS_FILE, 'r'))
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
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
        
        # Check if username exists
        if not username_exists(username):
            return render_template('login.html', error='Username not found. Please sign up first.')
        
        # Verify password
        users = load_users()
        if users[username] != password:
            return render_template('login.html', error='Incorrect password. Please try again.')
        
        # Successful login
        return render_template('login.html', success='Login successful!')
    
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate inputs
        if not username or not password:
            return render_template('signup.html', error='Username and password are required')
        
        # Check if username already exists
        if username_exists(username):
            return render_template('signup.html', error='Username already exists. Please choose a different username.')
        
        # Save new user
        users = load_users()
        users[username] = password
        save_users(users)
        
        # Redirect to success
        return render_template('signup.html', success='Account created successfully! You can now log in.')
    
    return render_template('signup.html')


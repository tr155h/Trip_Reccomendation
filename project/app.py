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


def is_valid_username(username):
    """Validate username format (must end with 4 digits)"""
    if not username or len(username) < 5:
        return False
    # Check if last 4 characters are digits
    return username[-4:].isdigit()


def is_valid_password(password):
    """Validate password length (minimum 6 characters)"""
    return password and len(password) >= 6

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

        if not is_valid_password(password):
            return render_template('login.html', error='Password must be at least 6 characters long')

        # Load user record
        user = load_user(username)
        if not user:
            return render_template('login.html', error='Username not found. Please sign up first.')

        # Verify password (check hashed password)
        if not check_password_hash(user['password'], password):
            return render_template('login.html', error='Incorrect password. Please try again.')

        session['username'] = username
        return redirect(url_for('profile'))

    # If GET, allow optional success message and prefilled username from query params
    success = request.args.get('success')
    prefill = request.args.get('username')
    return render_template('login.html', success=success, username=prefill)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirmPassword', '').strip()

        # Validate inputs
        if not username or not password or not confirm_password:
            return render_template('signup.html', error='Username and passwords are required')

        if not is_valid_username(username):
            return render_template('signup.html', error='Username must end with 4 digits (e.g., michael1234)')

        if not is_valid_password(password):
            return render_template('signup.html', error='Password must be at least 6 characters long')

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

        # After creating account, redirect user to login so they can sign in
        return redirect(url_for('login', success='Account created. Please log in.', username=username))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    user = load_user(username)
    saved_trips = user.get('trips', []) if user else []
    return render_template('profile.html', username=username, saved_trips=saved_trips)


@app.route('/input', methods=['GET'])
def input_page():
    # Render the trip input page. day is expected as a query parameter.
    day = request.args.get('day', '1')
    try:
        day_val = int(day)
    except (ValueError, TypeError):
        day_val = 1
    return render_template('input.html', day=day_val)



@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    # Ensure user is logged in
    username = session.get('username')
    if not username:
        return redirect(url_for('login', error='Please log in to create a trip'))

    trip_name = request.form.get('tripName', '').strip()
    city = request.form.get('city', '').strip()
    budget = request.form.get('budget', '').strip()
    day = request.form.get('day', '1')
    try:
        day_val = int(day)
    except (ValueError, TypeError):
        day_val = 1

    # categories sent as multiple select
    categories = request.form.getlist('category')

    # Basic validation
    if not trip_name or not city or not budget:
        return render_template('input.html', day=day_val, error='Trip name, city and budget are required')

    try:
        budget_val = float(budget)
    except ValueError:
        return render_template('input.html', day=day_val, error='Invalid budget value')

    if not categories or len(categories) == 0:
        return render_template('input.html', day=day_val, error='Please select at least one category')
    if len(categories) > 3:
        return render_template('input.html', day=day_val, error='Please select no more than 3 categories')

    # Load users, append trip to user's trips
    users = load_users()
    user = users.get(username)
    if user is None:
        return redirect(url_for('login', error='User not found. Please log in.'))

    user = user if isinstance(user, dict) else {'password': user, 'trips': []}
    user.setdefault('trips', [])

    # Create trip object
    trip = {
        'day': day_val,
        'name': trip_name,
        'city': city,
        'budget': budget_val,
        'categories': categories
    }

    # If a trip for this day already exists, replace it, else append
    replaced = False
    for i, t in enumerate(user['trips']):
        if t.get('day') == day_val:
            user['trips'][i] = trip
            replaced = True
            break
    if not replaced:
        user['trips'].append(trip)

    users[username] = user
    save_users(users)

    return redirect(url_for('profile'))



if __name__ == '__main__':
    app.run(debug=True)
#Main Flask app, routes and logic for the web application
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Path to users.json file
USERS_FILE = os.path.join(os.path.dirname(__file__), '../Data/users.json')
CITY_DATA_FILE = os.path.join(os.path.dirname(__file__), '../Data/city_data.json')

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

def load_city_data():
    """Load city data from JSON file"""
    if os.path.exists(CITY_DATA_FILE):
        try:
            with open(CITY_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except:
            pass
    return {}

def save_city_data(city_data):
    """Save city data to JSON file"""
    with open(CITY_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(city_data, f, indent=2)

def add_city_to_database(city_name):
    """Add a new city to city_data.json if it doesn't exist"""
    city_data = load_city_data()
    city_name_lower = city_name.lower()
    
    # Check if city already exists (case-insensitive)
    for existing_city in city_data.keys():
        if existing_city.lower() == city_name_lower:
            return True
    
    # Add new city with empty places list
    city_data[city_name] = {
        'name': city_name,
        'places': [],
        'categories': []
    }
    save_city_data(city_data)
    return True

def get_recommendations(city, budget, categories):
    """Generate recommendations based on city, budget, and categories
    Returns a list of recommended places within budget"""
    
    # Sample database of places by category and approximate cost
    sample_places = {
        'Food': [
            {'name': 'Street Food Tour', 'category': 'Food', 'cost': 8, 'duration': '1.5 hours', 'description': 'Explore local street food'},
            {'name': 'Local Restaurant', 'category': 'Food', 'cost': 15, 'duration': '1.5 hours', 'description': 'Traditional local cuisine'},
            {'name': 'Fine Dining Experience', 'category': 'Food', 'cost': 45, 'duration': '2.5 hours', 'description': 'Upscale dining experience'},
            {'name': 'Food Market Tour', 'category': 'Food', 'cost': 12, 'duration': '2 hours', 'description': 'Visit local food markets'}
        ],
        'Shopping': [
            {'name': 'Local Market', 'category': 'Shopping', 'cost': 20, 'duration': '2 hours', 'description': 'Browse local shops'},
            {'name': 'Shopping District', 'category': 'Shopping', 'cost': 50, 'duration': '3 hours', 'description': 'Main shopping district'},
            {'name': 'Souvenir Shops', 'category': 'Shopping', 'cost': 25, 'duration': '1.5 hours', 'description': 'Find local souvenirs'},
            {'name': 'Night Market', 'category': 'Shopping', 'cost': 30, 'duration': '3 hours', 'description': 'Evening shopping markets'}
        ],
        'Culture/History': [
            {'name': 'Museum Visit', 'category': 'Culture/History', 'cost': 12, 'duration': '2 hours', 'description': 'Local history museum'},
            {'name': 'Ancient Temple Tour', 'category': 'Culture/History', 'cost': 8, 'duration': '1.5 hours', 'description': 'Historical temple exploration'},
            {'name': 'Art Gallery', 'category': 'Culture/History', 'cost': 10, 'duration': '1.5 hours', 'description': 'Contemporary and traditional art'},
            {'name': 'Heritage Site', 'category': 'Culture/History', 'cost': 20, 'duration': '2.5 hours', 'description': 'UNESCO heritage sites'}
        ],
        'Sightseeing': [
            {'name': 'City Viewpoint', 'category': 'Sightseeing', 'cost': 5, 'duration': '1 hour', 'description': 'Panoramic city views'},
            {'name': 'City Walking Tour', 'category': 'Sightseeing', 'cost': 18, 'duration': '2 hours', 'description': 'Guided walking tour'},
            {'name': 'Nature Park Visit', 'category': 'Sightseeing', 'cost': 0, 'duration': '2 hours', 'description': 'Beautiful nature trails'},
            {'name': 'Scenic Photography Tour', 'category': 'Sightseeing', 'cost': 25, 'duration': '3 hours', 'description': 'Photo tour of highlights'}
        ]
    }
    
    recommendations = []
    
    # Generate recommendations from sample data based on selected categories
    for category in categories:
        if category in sample_places:
            for place in sample_places[category]:
                # Only add if within budget and not already added
                if place['cost'] <= budget:
                    # Check if already added
                    if not any(r['name'] == place['name'] for r in recommendations):
                        recommendations.append(place)
    
    # Sort by cost (cheapest first) and return top 10
    recommendations.sort(key=lambda x: x['cost'])
    return recommendations[:10]



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

        # Verify password - handle both hashed and plain text passwords for backwards compatibility
        stored_password = user['password']
        if stored_password.startswith('scrypt:'):  # Hashed password format
            if not check_password_hash(stored_password, password):
                return render_template('login.html', error='Incorrect password. Please try again.')
        else:  # Plain text password (legacy format)
            if stored_password != password:
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
    # Read username if present; allow anonymous users to generate a plan (won't be saved)
    username = session.get('username')

    # Debug log incoming form and session keys
    try:
        app.logger.info('generate_plan called by user: %s', username)
        app.logger.info('form keys: %s', list(request.form.keys()))
        app.logger.info('session keys: %s', list(session.keys()))
    except Exception:
        pass

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
        if budget_val < 0:
            return render_template('input.html', day=day_val, error='Budget must be a positive number')
    except ValueError:
        return render_template('input.html', day=day_val, error='Invalid budget value')

    if not categories or len(categories) == 0:
        return render_template('input.html', day=day_val, error='Please select at least one category')
    if len(categories) > 3:
        return render_template('input.html', day=day_val, error='Please select no more than 3 categories')

    # Add city to database if new
    add_city_to_database(city)
    
    # Generate recommendations based on budget, city, and categories
    recommendations = get_recommendations(city, budget_val, categories)

    # Load users, append trip to user's trips
    users = load_users()
    user = users.get(username)
    if user is None:
        return redirect(url_for('login', error='User not found. Please log in.'))

    user = user if isinstance(user, dict) else {'password': user, 'trips': []}
    user.setdefault('trips', [])

    # Create trip object with recommendations
    trip = {
        'day': day_val,
        'name': trip_name,
        'city': city,
        'budget': budget_val,
        'categories': categories,
        'recommendations': recommendations
    }

    # If user is logged in, save trip to their account; otherwise just keep it in session
    if username:
        users = load_users()
        user = users.get(username)
        if user is None:
            # If user disappeared, fall back to anonymous flow
            session['last_trip'] = trip
            session['saved'] = False
            return redirect(url_for('results'))

        user = user if isinstance(user, dict) else {'password': user, 'trips': []}
        user.setdefault('trips', [])

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
        session['last_trip'] = trip
        session['saved'] = True

        # Render results immediately so user lands on results page after submitting
        activities = []
        transport_cost = 0.0
        total_cost = trip.get('budget', 0.0)
        chart_data = ''
        return render_template(
            'result.html',
            trip_name=trip.get('name', ''),
            day=trip.get('day', 1),
            budget=trip.get('budget', 0.0),
            activities=activities,
            transport_cost=transport_cost,
            total_cost=total_cost,
            chart_data=chart_data
        )

    # Anonymous (not logged in): do not save to users.json, but render results for viewing
    session['last_trip'] = trip
    session['saved'] = False
    activities = []
    transport_cost = 0.0
    total_cost = trip.get('budget', 0.0)
    chart_data = ''
    return render_template(
        'result.html',
        trip_name=trip.get('name', ''),
        day=trip.get('day', 1),
        budget=trip.get('budget', 0.0),
        activities=activities,
        transport_cost=transport_cost,
        total_cost=total_cost,
        chart_data=chart_data
    )


@app.route('/results')
def results():
    # Render results page using last generated trip stored in session
    app.logger.info('results called; session keys: %s', list(session.keys()))
    trip = session.get('last_trip')
    if not trip:
        return redirect(url_for('profile'))

    recommendations = session.get('recommendations', [])
    total_cost = session.get('total_cost', 0)
    
    # Calculate transport estimate (default 10-15% of budget or $5 minimum)
    transport_cost = max(5, trip.get('budget', 0) * 0.1)
    
    # Convert recommendations to format for result.html
    activities = []
    for i, rec in enumerate(recommendations):
        activities.append({
            'title': rec.get('name', ''),
            'place': trip.get('city', ''),
            'description': rec.get('description', ''),
            'price': rec.get('cost', 0),
            'food': rec.get('category', ''),
            'image_url': 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22260%22 height=%22170%22%3E%3Crect fill=%22%234b79a1%22 width=%22260%22 height=%22170%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2220%22 fill=%22white%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3E{title}%3C/text%3E%3C/svg%3E'.format(title=rec.get('name', '')[:20])
        })

    return render_template(
        'result.html',
        trip_name=trip.get('name', ''),
        day=trip.get('day', 1),
        budget=trip.get('budget', 0.0),
        activities=activities,
        transport_cost=transport_cost,
        total_cost=total_cost + transport_cost,
        chart_data=''
    )



if __name__ == '__main__':
    app.run(debug=True)
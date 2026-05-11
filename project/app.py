#Main Flask app, routes and logic for the web application
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from data_handler import load_json_file_safe, save_json_file

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')

# Path to users.json file
USERS_FILE = os.path.join(os.path.dirname(__file__), '../Data/users.json')
CITY_DATA_FILE = os.path.join(os.path.dirname(__file__), '../Data/city_data.json')
FORUM_FILE = os.path.join(os.path.dirname(__file__), '../Data/forum.json')

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
        except (json.JSONDecodeError, IOError) as e:
            app.logger.error(f"Failed to load city data: {e}")
    return {}


def activity_image_url(rec):
    """Use the saved static image path, or fall back to a simple placeholder."""
    if rec.get('image_url'):
        return rec.get('image_url')

    title = rec.get('name', '')[:20]
    return 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22260%22 height=%22170%22%3E%3Crect fill=%22%234b79a1%22 width=%22260%22 height=%22170%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2220%22 fill=%22white%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3E{title}%3C/text%3E%3C/svg%3E'.format(title=title)

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

#forums
def load_forum():
    """Load forum posts from JSON file"""
    if os.path.exists(FORUM_FILE):
        try:
            with open(FORUM_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            app.logger.error(f"Failed to load forum data: {e}")
    return []

def save_forum(posts):
    """Save forum posts to JSON file"""
    with open(FORUM_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2)

def add_forum_post(username, title, content, city=None):
    """Add a new forum post"""
    posts = load_forum()
    new_post = {
        'id': len(posts) + 1,
        'username': username,
        'title': title,
        'content': content,
        'city': city,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'replies': []
    }
    posts.append(new_post)
    save_forum(posts)
    return new_post

def add_reply_to_post(post_id, username, content):
    """Add a reply to a forum post"""
    posts = load_forum()
    for post in posts:
        if post['id'] == post_id:
            reply = {
                'username': username,
                'content': content,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            post['replies'].append(reply)
            save_forum(posts)
            return True
    
    # Post not found
    app.logger.warning(f"Forum post {post_id} not found when adding reply")
    return False
    return False

#reccomendations
def get_recommendations_for_city(city, budget, categories):
    """Generate recommendations using recommender module with city_data"""
    from recommender import get_recommendations
    
    # Load city data from JSON using data_handler
    city_data = load_city_data()
    
    # City must exist in database (enforced by dropdown in UI)
    if city not in city_data:
        app.logger.error(f"City {city} not found in database")
        return []
    
    city_info = city_data[city]
    places = city_info.get('places', [])
    
    # Should always have places for city in data
    if not places:
        app.logger.error(f"No places found for {city}")
        return []
    
    # Generate recommendations from actual city data
    recommendations = get_recommendations(city, budget, categories, places)
    
    app.logger.info(f"Generated {len(recommendations)} recommendations for {city}")
    return recommendations





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

        # Verify password - all passwords must be hashed
        stored_password = user['password']
        if not check_password_hash(stored_password, password):
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
    # Render the trip input page. trip_name and day are expected as query parameters.
    trip_name = request.args.get('trip_name')
    day = request.args.get('day', '1')
    try:
        day_val = int(day)
    except (ValueError, TypeError):
        day_val = 1
    
    # Validate day_val is not None
    if day_val is None:
        day_val = 1
    
    city_data = load_city_data()
    available_cities = list(city_data.keys())
    return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities)


@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    """Page to create a new trip with a custom name"""
    if request.method == 'POST':
        trip_name = request.form.get('tripName', '').strip()
        
        if not trip_name:
            return render_template('create_trip.html', error='Trip name is required')
        
        # Redirect to input page with the trip name
        return redirect(url_for('input_page', trip_name=trip_name, day='1'))
    
    return render_template('create_trip.html')



@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    # Get username from session (login required to reach this route)
    username = session.get('username')

    # Debug log incoming form and session keys
    try:
        app.logger.info('generate_plan called by user: %s', username)
        app.logger.info('form keys: %s', list(request.form.keys()))
        app.logger.info('session keys: %s', list(session.keys()))
    except Exception:
        pass

    trip_name = request.form.get('tripName', '').strip()   # Name of the trip
    city = request.form.get('city', '').strip()
    budget = request.form.get('budget', '').strip()
    day = request.form.get('day', '1')
    try:
        day_val = int(day)
    except (ValueError, TypeError):
        day_val = 1
    
    # Validate day_val is not None
    if day_val is None:
        day_val = 1

    # categories sent as multiple select
    categories = request.form.getlist('category')
    city_data = load_city_data()
    available_cities = list(city_data.keys())

    # Basic validation
    if not city or not budget or not trip_name:
        return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='All fields are required')

    try:
        budget_val = float(budget)
        if budget_val < 0:
            return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='Budget must be a positive number')
    except ValueError:
        return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='Invalid budget value')

    if not categories or len(categories) == 0:
        return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='Please select at least one category')
    if len(categories) > 3:
        return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='Please select no more than 3 categories')
    
    # Generate recommendations based on budget, city, and categories
    # Recommender will reserve $25 under budget
    recommendations = get_recommendations_for_city(city, budget_val, categories)

    # Validate that the selected city exists in our database
    if city not in available_cities:
        return render_template('input.html', trip_name=trip_name, day=day_val, available_cities=available_cities, error='Please select a city from the available options')

    # Create day plan object with recommendations
    categories_str = ', '.join(categories)
    day_plan = {
        'day': day_val,
        'name': categories_str,
        'city': city,
        'budget': budget_val,
        'categories': categories,
        'recommendations': recommendations
    }

    # If user is logged in, save day plan to their account
    if username:
        users = load_users()
        user = users.get(username)
        if user is None:
            # If user disappeared, fall back to anonymous flow
            session['last_trip'] = day_plan
            session['saved'] = False
            return redirect(url_for('results'))

        user = user if isinstance(user, dict) else {'password': user, 'trips': []}
        user.setdefault('trips', [])

        # Find or create the trip with this trip_name
        trip = None
        for t in user['trips']:
            if t.get('trip_name') == trip_name:
                trip = t
                break
        
        if trip is None:
            # Create new trip
            trip = {
                'trip_name': trip_name,
                'days': {}
            }
            user['trips'].append(trip)
        
        # Add or replace the day plan
        trip['days'][str(day_val)] = day_plan

        users[username] = user
        save_users(users)
        session['last_trip'] = day_plan
        session['trip_name'] = trip_name
        session['recommendations'] = recommendations
        session['saved'] = True

        # Convert recommendations to format for result.html
        activities = []
        for rec in recommendations:
            activities.append({
                'title': rec.get('name', ''),
                'place': city,
                'description': rec.get('description', ''),
                'price': rec.get('cost', 0),
                'food': rec.get('category', ''),
                'image_url': activity_image_url(rec)
            })
        
        # Calculate transport estimate (10% of activities cost or $5 minimum)
        total_activities_cost = sum(rec.get('cost', 0) for rec in recommendations)
        transport_cost = max(5, total_activities_cost * 0.1)
        total_cost = total_activities_cost + transport_cost
        
        # Render results immediately so user lands on results page after submitting
        return render_template(
            'result.html',
            plan_name=categories_str,
            trip_name=trip_name,
            day=day_val,
            budget=budget_val,
            activities=activities,
            transport_cost=transport_cost,
            total_cost=total_cost,
            chart_data=''
        )


@app.route('/view_plan')
def view_plan():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    trip_name = request.args.get('trip_name')
    day = request.args.get('day', '1')
    try:
        day_val = int(day)
    except (ValueError, TypeError):
        day_val = 1
    
    # Validate day_val is not None
    if day_val is None:
        day_val = 1

    if not trip_name:
        return redirect(url_for('profile'))

    user = load_user(username)
    if not user:
        return redirect(url_for('profile'))

    trips = user.get('trips', [])
    trip = None
    for t in trips:
        if t.get('trip_name') == trip_name:
            trip = t
            break

    if not trip:
        return redirect(url_for('profile'))

    # Get the specific day plan
    day_plan = trip.get('days', {}).get(str(day_val))
    
    # Validate day_plan exists before accessing it
    if not day_plan:
        app.logger.warning(f"Day plan not found for trip {trip_name} day {day_val}")
        return redirect(url_for('profile'))

    # Get recommendations from the saved day plan
    recommendations = day_plan.get('recommendations', [])
    city = day_plan.get('city', '')
    budget = day_plan.get('budget', 0.0)
    plan_name = day_plan.get('name', '')
    
    # Convert recommendations to format for result.html
    activities = []
    for rec in recommendations:
        activities.append({
            'title': rec.get('name', ''),
            'place': city,
            'description': rec.get('description', ''),
            'price': rec.get('cost', 0),
            'food': rec.get('category', ''),
            'image_url': activity_image_url(rec)
        })
    
    # Calculate transport estimate ($25 reserve as promised)
    transport_cost = 25
    total_activities_cost = sum(rec.get('cost', 0) for rec in recommendations)
    total_cost = total_activities_cost + transport_cost
    
    # Render the result view for the saved trip
    return render_template(
        'result.html',
        plan_name=plan_name,
        trip_name=trip_name,
        day=day_val,
        budget=budget,
        activities=activities,
        transport_cost=transport_cost,
        total_cost=total_cost,
        chart_data=''
    )


@app.route('/results')
def results():
    # Render results page using last generated trip stored in session
    app.logger.info('results called; session keys: %s', list(session.keys()))
    day_plan = session.get('last_trip')
    if not day_plan:
        return redirect(url_for('profile'))

    recommendations = session.get('recommendations', [])
    total_cost = session.get('total_cost', 0)
    
    # Calculate transport estimate (default 10-15% of budget or $5 minimum)
    transport_cost = max(5, day_plan.get('budget', 0) * 0.1)
    
    # Convert recommendations to format for result.html
    activities = []
    for i, rec in enumerate(recommendations):
        activities.append({
            'title': rec.get('name', ''),
            'place': day_plan.get('city', ''),
            'description': rec.get('description', ''),
            'price': rec.get('cost', 0),
            'food': rec.get('category', ''),
            'image_url': activity_image_url(rec)
        })

    return render_template(
        'result.html',
        plan_name=day_plan.get('name', ''),
        trip_name=session.get('trip_name', 'Trip'),
        day=day_plan.get('day', 1),
        budget=day_plan.get('budget', 0.0),
        activities=activities,
        transport_cost=transport_cost,
        total_cost=total_cost + transport_cost,
        chart_data=''
    )



@app.route('/forum', methods=['GET'])
def forum():
    """Display forum page with all posts"""
    username = session.get('username')
    city_filter = request.args.get('city', '')
    
    posts = load_forum()
    
    # Filter by city if specified
    if city_filter:
        posts = [p for p in posts if p.get('city', '').lower() == city_filter.lower()]
    
    # Sort by most recent first
    posts = sorted(posts, key=lambda x: x['created_at'], reverse=True)
    
    return render_template(
        'forum.html',
        posts=posts,
        username=username,
        city_filter=city_filter
    )


@app.route('/forum/post', methods=['POST'])
def create_forum_post():
    """Create a new forum post"""
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    city = request.form.get('city', '').strip()
    
    # Validate input
    if not title:
        app.logger.warning(f"Forum post creation attempted without title by {username}")
        return render_template('forum.html', posts=load_forum(), username=username, error='Post title is required')
    
    if not content:
        app.logger.warning(f"Forum post creation attempted without content by {username}")
        return render_template('forum.html', posts=load_forum(), username=username, error='Post content is required')
    
    add_forum_post(username, title, content, city)
    app.logger.info(f"Forum post created by {username}: {title}")
    return redirect(url_for('forum'))


@app.route('/forum/reply/<int:post_id>', methods=['POST'])
def reply_to_post(post_id):
    """Add a reply to a forum post"""
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    content = request.form.get('reply_content', '').strip()
    
    if not content:
        app.logger.warning(f"Forum reply attempted without content by {username} on post {post_id}")
        return render_template('forum.html', posts=load_forum(), username=username, error='Reply content is required')
    
    success = add_reply_to_post(post_id, username, content)
    if not success:
        app.logger.error(f"Failed to add reply to post {post_id}: post not found")
        return render_template('forum.html', posts=load_forum(), username=username, error='Post not found. Your reply could not be added.')
    
    app.logger.info(f"Reply added by {username} to post {post_id}")
    return redirect(url_for('forum'))


if __name__ == '__main__':
    app.run(debug=True)

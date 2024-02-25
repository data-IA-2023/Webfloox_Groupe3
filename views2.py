from flask import Flask, redirect, request, jsonify, render_template, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from models import HybridRecommender
import bcrypt  # For password hashing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, unique secret key

# Load data (assuming data files are present)
ratings_data = pd.read_csv('ratings.csv')
imdb_data = pd.read_csv('imdb_data.csv')

# Create recommender instance
hybrid_recommender = HybridRecommender(ratings_data, imdb_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate user input (e.g., username length, password complexity)
        # ...

        # Hash password securely using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user data in a secure database (replace with your database connection and logic)
        # ...

        session['username'] = username
        return redirect('/profile')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user data from database (replace with your database logic)
        # ...

        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]['password']):
            session['username'] = username
            return redirect('/profile')
        else:
            # Handle invalid login credentials securely (e.g., rate limiting, error message)
            return 'Invalid login credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/profile')
def profile():
    if not 'username' in session:
        return redirect('/login')

    user_id = 1  # Replace with logic to retrieve actual user ID from database or session

    # Get recommendations
    collab_user_recs = hybrid_recommender.collaborative_filtering_user(user_id)
    collab_item_recs = hybrid_recommender.collaborative_filtering_item(user_id)
    content_based_recs = hybrid_recommender.content_based_recommendation(user_id)

    # Fusionner et classer les recommandations
    all_recs = collab_user_recs + collab_item_recs + content_based_recs
    unique_recs = []
    [unique_recs.append(x) for x in all_recs if x not in unique_recs]
    rec_counter = Counter(all_recs)
    sorted_recs = sorted(unique_recs, key=lambda x: rec_counter[x], reverse=True)
    top_n = 5
    final_recommendations = sorted_recs[:top_n]

    return render_template('profile.html', recommendations=final_recommendations)

# ... (rest of the code remains the same)

if __name__ == '__main__':
    app.run(debug=True)

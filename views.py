from flask import Flask, redirect, request, jsonify, render_template, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from models import HybridRecommender
from users import db, User 
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv('BDD_URL.env')
BDD_URL = os.environ['BDD_URL']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = BDD_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'  # Clé secrète pour la gestion de session
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Crée un nouvel utilisateur
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect('/login')
        except IntegrityError:
            db.session.rollback()
            return "Ce nom d'utilisateur existe déjà. Veuillez choisir un autre nom d'utilisateur."
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérifie les informations d'identification
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Connecte l'utilisateur (vous pouvez ajouter la gestion de session ici)
            session['user_id'] = user.id
            return redirect('/profile')
        else:
            return "Nom d'utilisateur ou mot de passe incorrect."

    return render_template('login.html')

@app.route('/profile')
def profile():
    # Vérifie si l'utilisateur est connecté
    if 'user_id' not in session:
        return redirect('/login')

    # Récupérer l'ID utilisateur à partir de la session
    user_id = session['user_id']

    # Obtenir les recommandations pour l'utilisateur connecté
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

    # Renvoyer les recommandations à la page de profil
    return render_template('profile.html', recommendations=final_recommendations)

# Chargement des données utilisateur-film
ratings_data = pd.read_csv('ratings.csv')

# Chargement des données IMDb (exemple de caractéristiques des films)
imdb_data = pd.read_csv('imdb_data.csv')

# Create an instance of the recommender
hybrid_recommender = HybridRecommender(ratings_data, imdb_data)

if __name__ == '__main__':
    app.run(debug=True)

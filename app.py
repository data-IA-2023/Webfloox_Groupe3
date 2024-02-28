
from flask import Flask, redirect, request, jsonify, render_template, session
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from cleanDF import cleandf
from models import HybridRecommender
from users import db, User 
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from tmdb import get_movie_poster_url
    
load_dotenv('BDD_URL.env')
BDD_URL = os.environ['BDD_URL']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = BDD_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '123'  # Clé secrète pour la gestion de session
db.init_app(app)

hybrid_recommender = None
def loaddata():
    global hybrid_recommender
    # Connexion à la base de données
    engine = create_engine(BDD_URL)
    SQLimdb= """
    SELECT  "tconst", "primaryTitle", "titleType", "isAdult", "startYear", "runtimeMinutes", "genres", "averageRating", "directors", "writers", "actor", "producer", "cinematographer", "composer", "editor", "production_designer", "self", "archive_footage", "archive_sound"
    from "castview"
    where "titleType" = 'movie' and "runtimeMinutes" < 360 and "runtimeMinutes" Is NOT null and "averageRating" is NOT NULL and "genres" is NOT NULL and "startYear" is NOT NULL and "isAdult" is NOT NULL  and "directors" is NOT NULL and  "writers" is NOT NULL  and  "actor" is NOT NULL  and  "producer" is NOT NULL
    ORDER BY "averageRating"  desc
    limit 1000;
    """
    #, "startYear"
    
    SQLratings= """
    SELECT * from "ratings";
    """
    # Chargement des données utilisateur-film
    ratings_data = pd.read_sql(SQLratings, engine)
    imdb_data = pd.read_sql(SQLimdb, engine)
    c=cleandf()
    imdb_data=c.clean(imdb_data)
    # Create an instance of the recommender
    hybrid_recommender = HybridRecommender(ratings_data, imdb_data)




@app.route('/')
def index():
    global hybrid_recommender
    if hybrid_recommender is None:
        loaddata()
        
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérifie si le nom d'utilisateur existe déjà dans la base de données
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html',error="Ce nom d'utilisateur existe déjà. Veuillez choisir un autre nom d'utilisateur.")
        
        # Crée un nouvel utilisateur
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect('/login')
        except IntegrityError:
            db.session.rollback()
            return render_template('signup.html',error="Une erreur s'est produite lors de la création de votre compte. Veuillez réessayer.")
    return render_template('signup.html',error=None)


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
            return redirect('/profile?movie=1')
        else:
            return "Nom d'utilisateur ou mot de passe incorrect."

    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Vérifie si l'utilisateur est connecté
    if 'user_id' not in session or session['user_id'] is None:
        return redirect('/login')

    # Récupérer l'ID utilisateur à partir de la session
    user_id = session['user_id']
    user = User.query.get(user_id)

    # Obtenir les recommandations pour l'utilisateur connecté
    collab_user_recs =[]
    collab_item_recs =[]
    # collab_user_recs = hybrid_recommender.collaborative_filtering_user(user_id)
    # collab_item_recs = hybrid_recommender.collaborative_filtering_item(user_id)
    
    content_based_recs=[]
    movieid=1
    if request.args.get('movie') != None: 
        movieid = int(request.args.get('movie'))
    print('movie = ' , movieid)
    content_based_recs = hybrid_recommender.content_based_recommendation(movieid)

    # Fusionner et classer les recommandations
    all_recs = collab_user_recs + collab_item_recs + content_based_recs
    unique_recs = []
    [unique_recs.append(x) for x in all_recs if x not in unique_recs]
    rec_counter = Counter(all_recs)
    sorted_recs = sorted(unique_recs, key=lambda x: rec_counter[x], reverse=True)
    top_n = 18
    final_recommendations = sorted_recs[:top_n]

    # Créer une liste de dictionnaires contenant les informations sur les recommandations
    recommendations_info = []
    for movie_id in final_recommendations:
        movie_link = get_movie_poster_url(movie_id)
        if movie_link is None:
            movie_link = "/static/image/nopicture.jpg"
        recommendations_info.append({"id": hybrid_recommender.getid(movie_id), "link": movie_link})
    
    film_selected= get_movie_poster_url(hybrid_recommender.findfilm(movieid)[0])
    
    # Renvoyer les informations sur les recommandations à la page de profil
    return render_template('profile.html', recommendations=recommendations_info, username=user.username, film=film_selected)



if __name__ == '__main__':
    app.run(debug=True)

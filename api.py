from flask import Flask, redirect, request, jsonify, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter

app = Flask(__name__)

# Chargement des données utilisateur-film
ratings_data = pd.read_csv('ratings.csv')

# Chargement des données IMDb (exemple de caractéristiques des films)
imdb_data = pd.read_csv('imdb_data.csv')

class HybridRecommender:
    def __init__(self, ratings_data, imdb_data):
        self.ratings_data = ratings_data
        self.imdb_data = imdb_data
        
    def collaborative_filtering_user(self, user_id, top_n=5):
        # Filtrage collaboratif basé sur les utilisateurs
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        similar_users = self.find_similar_users(user_id)
        
        recommended_movies = []
        for similar_user in similar_users:
            similar_user_ratings = self.ratings_data[self.ratings_data['userId'] == similar_user]
            movies_not_seen = similar_user_ratings[~similar_user_ratings['movieId'].isin(user_ratings['movieId'])]
            recommended_movies.extend(movies_not_seen['movieId'].tolist())
        
        return recommended_movies[:top_n]
    
    def collaborative_filtering_item(self, user_id, top_n=5):
        # Filtrage collaboratif basé sur les éléments
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        
        similar_items = []
        for movie_id in user_ratings['movieId'].tolist():
            similar_items.extend(self.find_similar_items(movie_id))
        
        return similar_items[:top_n]
    
    def content_based_recommendation(self, user_id, top_n=5):
        # Recommandation basée sur le contenu (exemple avec similarité cosinus)
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        user_preferences = user_ratings.merge(self.imdb_data, on='movieId', how='inner')
        
        # Calcul de la similarité entre les films basée sur les caractéristiques (exemple: genres, acteurs, réalisateurs)
        similarity_matrix = cosine_similarity(user_preferences.drop(columns=['userId', 'movieId']))
        
        # Recommandation des films similaires aux films préférés de l'utilisateur
        recommended_movies = []
        for movie_id in user_preferences['movieId'].tolist():
            movie_index = user_preferences[user_preferences['movieId'] == movie_id].index[0]
            similar_movies = self.find_similar_movies(similarity_matrix, movie_index)
            recommended_movies.extend(similar_movies)
        
        return recommended_movies[:top_n]
    
    def find_similar_users(self, user_id, k=5):
        # Exemple: trouver des utilisateurs similaires basés sur les évaluations
        # Utilisez une technique comme Nearest Neighbors pour trouver des utilisateurs similaires
        nn_model = NearestNeighbors(n_neighbors=k, algorithm='auto')
        nn_model.fit(self.ratings_data.drop(columns=['userId', 'movieId']))
        user_index = self.ratings_data[self.ratings_data['userId'] == user_id].index[0]
        _, similar_user_indices = nn_model.kneighbors([self.ratings_data.drop(columns=['userId', 'movieId']).iloc[user_index]])
        similar_users = self.ratings_data.iloc[similar_user_indices[0]]['userId'].tolist()
        return similar_users
    
    def find_similar_items(self, movie_id, k=5):
        # Exemple: trouver des films similaires basés sur les évaluations
        # Utilisez une technique comme Nearest Neighbors pour trouver des films similaires
        nn_model = NearestNeighbors(n_neighbors=k, algorithm='auto')
        nn_model.fit(self.ratings_data.drop(columns=['userId', 'movieId']))
        movie_index = self.ratings_data[self.ratings_data['movieId'] == movie_id].index[0]
        _, similar_movie_indices = nn_model.kneighbors([self.ratings_data.drop(columns=['userId', 'movieId']).iloc[movie_index]])
        similar_movies = self.ratings_data.iloc[similar_movie_indices[0]]['movieId'].tolist()
        return similar_movies
    
    def find_similar_movies(self, similarity_matrix, movie_index):
        # Exemple: trouver des films similaires basés sur la matrice de similarité
        # Dans cet exemple, nous recommandons les films les plus similaires à un film donné
        similar_movies_indices = similarity_matrix[movie_index].argsort()[::-1]
        similar_movies = self.ratings_data.iloc[similar_movies_indices]['movieId'].tolist()
        return similar_movies

# Création d'une instance du système de recommandation hybride
hybrid_recommender = HybridRecommender(ratings_data, imdb_data)

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Page d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Traiter les données d'inscription ici
        # Rediriger vers la page de connexion après l'inscription réussie
        return redirect('/login')
    return render_template('signup.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Traiter les données de connexion ici
        # Rediriger vers la page de profil après la connexion réussie
        return redirect('/profile')
    return render_template('login.html')

# Page de profil utilisateur
@app.route('/profile')
def profile():
    # Récupérer l'ID utilisateur à partir de la session ou des données de connexion
    user_id = 1  # Exemple : utilisateur connecté avec l'ID 1
    
    # Obtenez les recommandations pour l'utilisateur connecté
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

if __name__ == '__main__':
    app.run(debug=True)

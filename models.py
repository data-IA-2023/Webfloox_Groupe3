from flask import Flask, redirect, request, jsonify, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter


class HybridRecommender:
    def __init__(self, ratings_data, imdb_data):
        ratings_data['movieId'] = ratings_data['movieId'].astype(str)
        self.ratings_data = ratings_data
        imdb_data=imdb_data.dropna()
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
        # Recommendation based on content (example with cosine similarity)
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        user_preferences = pd.concat([user_ratings, self.imdb_data], axis=1)  # or 0
        
        user_preferences.dropna()
        
        # Calculating similarity between movies based on features (e.g., year)
        similarity_matrix = cosine_similarity(user_preferences['startYear'].values.reshape(-1, 1))
        
        # Recommendation of movies similar to user's preferred movies
        recommended_movies = []
        for idx in user_preferences.index:
            movie_id = user_preferences.loc[idx, 'movieId']
            similar_movies = self.find_similar_movies(similarity_matrix, idx)
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
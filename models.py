from flask import Flask, redirect, request, jsonify, render_template
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer

class HybridRecommender:
    
    def __init__(self, ratings_data, imdb_data):
        ratings_data['movieId'] = ratings_data['movieId'].astype(str)
        self.ratings_data = ratings_data
        
        self.imdb_data = imdb_data
        
    def collaborative_filtering_user(self, user_id, top_n=18):
        # Filtrage collaboratif basé sur les utilisateurs
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        similar_users = self.find_similar_users(user_id)
        
        recommended_movies = []
        for similar_user in similar_users:
            similar_user_ratings = self.ratings_data[self.ratings_data['userId'] == similar_user]
            movies_not_seen = similar_user_ratings[~similar_user_ratings['movieId'].isin(user_ratings['movieId'])]
            recommended_movies.extend(movies_not_seen['movieId'].tolist())
        
        return recommended_movies[:top_n]
    
    def collaborative_filtering_item(self, user_id, top_n=18):
        # Filtrage collaboratif basé sur les éléments
        user_ratings = self.ratings_data[self.ratings_data['userId'] == user_id]
        
        similar_items = []
        for movie_id in user_ratings['movieId'].tolist():
            similar_items.extend(self.find_similar_items(movie_id))
        
        return similar_items[:top_n]
    
    def content_based_recommendation(self, indexfilm=1, Nbfilm=19):
        
        cv = CountVectorizer(analyzer="word")
        count_vect = cv.fit_transform(self.imdb_data['feature'])
        similarity_measure = cosine_similarity(count_vect, count_vect[indexfilm])
        indexes = self.index_list(similarity_measure, Nbfilm)
        indexes = indexes[1:]
        return self.imdb_data.iloc[indexes]['tconst'].tolist()


    
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
    
    def findfilm(self, index):
        if index < len(self.imdb_data):
            return self.imdb_data.iloc[index][['tconst', 'primaryTitle']].tolist()
        else:
            return None
        
    def index_list(self, similarity_measure, Nbfilm):
        sorted_indexes = sorted(enumerate(similarity_measure), key=lambda x: x[1], reverse=True)
        top_indexes = [index for index, _ in sorted_indexes[:Nbfilm]]
        return top_indexes
    
    def getindex(self,filmm):
        index_list = self.imdb_data[self.imdb_data['primaryTitle'] == filmm].index
        if len(index_list) > 0:
            return index_list[0]
        else:
            return None
    def getid(self,tconst):
        index_list = self.imdb_data[self.imdb_data['tconst'] == tconst].index
        if len(index_list) > 0:
            return index_list[0]
        else:
            return None
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import seaborn as sns ;
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class Recommendation:
    def __init__(self, df, film='', Nbfilm=5, method='knn'):
        self.df = self.clean(df)

        cv = CountVectorizer(analyzer="word")
        self.count_vect = cv.fit_transform(df['feature'])
        
        self.resultat= self.recommender(film=film, Nbfilm=Nbfilm, method=method)

    def liste_en_texte(self, lst):
        if isinstance(lst, list):
            return ' '.join(lst)
        else:
            return lst

    def cleanText(self, df):
        df.fillna('missing', inplace=True)
        df = df.str.replace(',', ' ')
        return df

    def BooleanToText(self, df):
        return df.apply(lambda x: 'True' if x == 1 else 'False')

    def DateToCategory(self, df):
        df.fillna(df.mean(), inplace=True)
        bins = list(range(1800, 2056, 5))
        labels = [f"between{start}and{start+4}" for start in range(1800, 2051, 5)]
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def RuntimeToCategory(self, df):
        df = df.astype(int)
        df.fillna(df.mean(), inplace=True)
        bins = list(range(0, 615, 15))
        labels = [f"runtime_Between{start}and{start+15}" for start in range(0, 600, 15)]
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def RatingToCategory(self, df):
        df.fillna(df.mean(), inplace=True)
        bins = list(range(0, 12, 2))
        labels = ['*', '**', '***', '****', '*****']
        return pd.cut(df, bins=bins, labels=labels, right=False)

    def listTostr(self, df):
        return df.apply(lambda x: ' '.join(map(str, x)))

    def crewmod(self, x, type):
        return ' '.join([type + '_' + name for name in x.split()])

    def getindex(self, filmm):
        index_list = self.df[self.df['primaryTitle'] == filmm].index
        if len(index_list) > 0:
            return index_list[0]
        else:
            return None

    def index_list(self, similarity_measure, Nbfilm):
        sorted_indexes = sorted(enumerate(similarity_measure), key=lambda x: x[1], reverse=True)
        top_indexes = [index for index, _ in sorted_indexes[:Nbfilm]]
        return top_indexes

    def clean(self, df):
        columns_to_clean = ['primaryTitle', 'titleType', 'genres', 'directors', 'writers', 
                            'actor', 'producer', 'cinematographer', 'composer', 'editor', 
                            'production_designer', 'self', 'archive_footage', 'archive_sound']

        for column in columns_to_clean:
            df[column] = self.cleanText(df[column])
            
        df['feature'] = df['primaryTitle'] + ' '

        df['feature'] += 'titleType_'+df['titleType'] + ' '

        df['feature'] += 'Rating_'+self.RatingToCategory(df['averageRating']).astype(str) + ' '

        df['feature'] += 'startYear_'+self.DateToCategory(df['startYear']).astype(str) + ' '

        df['feature'] += self.RuntimeToCategory(df['runtimeMinutes']).astype(str)+ ' '

        df['feature'] += df['genres'] + ' '

        df['feature'] += 'ADULT_'+self.BooleanToText(df['isAdult']).astype(str)+' '

        df['feature'] += df['directors'].apply(self.crewmod, type='directors').astype(str)+' '
        df['feature'] += df['writers'].apply(self.crewmod, type='writers').astype(str)+' '
        df['feature'] += df['actor'].apply(self.crewmod, type='actor').astype(str)+' '
        df['feature'] += df['producer'].apply(self.crewmod, type='producer').astype(str)+' '
        return df

    def findfilm(self, index):
        if index < len(self.df):
            return self.df.iloc[index][['tconst', 'primaryTitle']].tolist()
        else:
            return None

    def recommender(self, film='', Nbfilm=5, method='knn'):
        indexfilm = self.getindex(film)
        if indexfilm is None:
            return []

        if method == 'cosine':
            similarity_measure = cosine_similarity(self.count_vect, self.count_vect[indexfilm])
            indexes = self.index_list(similarity_measure, Nbfilm)
            indexes = indexes[1:]
        elif method == 'knn':
            nbrs = NearestNeighbors(n_neighbors=Nbfilm+1, algorithm='auto').fit(self.count_vect)
            distances, indexes = nbrs.kneighbors(self.count_vect[indexfilm])
            indexes = indexes.flatten()[1:]  
        else:
            raise ValueError("Invalid method. Choose either 'cosine' or 'knn'.")

        return [self.findfilm(idx) for idx in indexes]


def data_load():
    load_dotenv('BDD_URL.env')
    BDD_URL = os.environ['BDD_URL']
    engine = create_engine(BDD_URL)


    SQL= """
    SELECT  "tconst", "primaryTitle", "titleType", "isAdult", "startYear", "runtimeMinutes", "genres", "averageRating", "directors", "writers", "actor", "producer", "cinematographer", "composer", "editor", "production_designer", "self", "archive_footage", "archive_sound"
    from "castview"
    where "titleType" = 'movie' and "runtimeMinutes" Is NOT null and "averageRating" is NOT NULL and "genres" is NOT NULL and "startYear" is NOT NULL and "isAdult" is NOT NULL  and "directors" is NOT NULL and  "writers" is NOT NULL  and  "actor" is NOT NULL  and  "producer" is NOT NULL
    ORDER BY "tconst" desc
    limit 100;
    """
    df = pd.read_sql(SQL, engine)
    engine.dispose()
    return df

df = data_load()

for film in df['primaryTitle']:
    
    r = Recommendation(df, film=film, Nbfilm=5, method='knn')
    print(f"{film} >---> {r.resultat}")


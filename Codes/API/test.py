# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 08:59:33 2024

@author: naouf
"""


from fastapi import FastAPI,Request,Form,Cookie, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from tmdb import get_movie_poster_url
from recommandation import Recommendation
import pandas as pd
from dotenv import load_dotenv
import os




def data_load():
    load_dotenv('BDD_URL.env')
    BDD_URL = os.environ['BDD_URL']
    engine = create_engine(BDD_URL)
    
    SQL= """
    SELECT  "tconst", "primaryTitle", "titleType", "isAdult", "startYear", "runtimeMinutes", "genres", "averageRating", "directors", "writers", "actor", "producer", "cinematographer", "composer", "editor", "production_designer", "self", "archive_footage", "archive_sound"
    from "castview"
    where "titleType" = 'movie' and "runtimeMinutes" Is NOT null and "averageRating" is NOT NULL and "genres" is NOT NULL and "startYear" is NOT NULL and "isAdult" is NOT NULL  and "directors" is NOT NULL and  "writers" is NOT NULL  and  "actor" is NOT NULL  and  "producer" is NOT NULL
    ORDER BY "tconst" desc
    limit 10000;
    """
    df = pd.read_sql(SQL, engine)
    engine.dispose()
    return df
dico2={}

Film = "Takkar"
nbfilms = 5
df = data_load()
recom = Recommendation(df, film=Film, Nbfilm=nbfilms, method='knn')
for x in recom.resultat:
    tconst = x[0]  # Accéder à l'élément 0 du tuple
    url = get_movie_poster_url(tconst)  # Appelle la fonction pour obtenir l'URL
    dico2[tconst] = url
    for cle, valeur in dico2.items():
        if valeur is None:
            dico2[cle] = "https://img.freepik.com/vecteurs-premium/affiche-pour-film-bientot-disponible_664340-160.jpg"

print(dico2)
print(df)


    

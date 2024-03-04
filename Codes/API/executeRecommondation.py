from recommandation import Recommendation
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine


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

df = data_load()



    
r = Recommendation(df, film="Takkar", Nbfilm=2, method='knn')


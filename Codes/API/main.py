


from fastapi import FastAPI,Request,Form,Cookie, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from tmdb import get_movie_poster_url
from starlette.responses import JSONResponse
from recommandation import Recommendation
import pandas as pd
from dotenv import load_dotenv
import os






BDD_URL="postgresql://citus:floox2024!@c-groupe3.3i2a7yekjrai5q.postgres.cosmos.azure.com:5432/netfloox?sslmode=require"
engine = create_engine(BDD_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="templates")

dico={}


@app.get("/accueil")
def accueil(request:Request):
    with engine.begin() as connexion:
        query = text("""SELECT  "tconst" from "castview" where "titleType" = 'movie' and "runtimeMinutes" < 360 and "runtimeMinutes" Is NOT null and "averageRating" is NOT NULL and "genres" is NOT NULL and "startYear" is NOT NULL and "isAdult" is NOT NULL  and "directors" is NOT NULL and  "writers" is NOT NULL  and  "actor" is NOT NULL  and  "producer" is NOT NULL ORDER BY "runtimeMinutes", "startYear" desc limit 100;""")
        resultat = (connexion.execute(query))
        rows = resultat.fetchall() 
                
        for row in rows:
            tconst = row[0]  # Accéder à l'élément 0 du tuple
            url = get_movie_poster_url(tconst)  # Appelle la fonction pour obtenir l'URL
            dico[tconst] = url
            for cle, valeur in dico.items():
                if valeur is None:
                    dico[cle] = "https://img.freepik.com/vecteurs-premium/affiche-pour-film-bientot-disponible_664340-160.jpg"

    return templates.TemplateResponse(
        request=request, name="index.html", context={"dico":dico})

print()

@app.get("/inscription")
def button_connexion(request:Request):
        
    return templates.TemplateResponse(
        request=request, name="inscription.html")





    

@app.get("/recommandation")
def recom_form(request:Request):
    
        return templates.TemplateResponse(
        request=request, name="recommandation.html")
    
    


@app.post("/recommandation")
def recom(request:Request, Film: str = Form(), nbfilms: int = Form()):
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
    df = data_load()
    recom = Recommendation(df, film=Film, Nbfilm=nbfilms, method='knn')
    for x in recom.resultat:
        tconst = x[0]  # Accéder à l'élément 0 du tuple
        url = get_movie_poster_url(tconst)  # Appelle la fonction pour obtenir l'URL
        dico2[tconst] = url
        for cle, valeur in dico2.items():
            if valeur is None:
                dico2[cle] = "https://img.freepik.com/vecteurs-premium/affiche-pour-film-bientot-disponible_664340-160.jpg"
    
    


    
    return templates.TemplateResponse(
        request=request, name="affichagecom.html",context={"recom":recom,"dico2":dico2})





@app.post("/inscription")
async def soumettre_formulaire(request: Request, username: str = Form(), password: str = Form()):
    
        with engine.begin() as connexion:
            query = text("INSERT INTO public.usernaoufel (username, password) VALUES (:username, :password)")
            connexion.execute(query,{"username":username,"password":password})
            
        if request.state==200:
            message='wp tu t es inscrit'
            return templates.TemplateResponse(
                request=request, name="inscription.html",context={ "message":message})
        else:
            message = "Belek ca ne marche pas"
            
            return templates.TemplateResponse(
                request=request, name="inscription.html",context={ "message":message})
    
@app.get("/set-cookie/")
async def set_cookie():
    content = {"message": "Cookie défini avec succès"}
    response = JSONResponse(content=content)
    response.set_cookie(key="cookie-example", value="cookie-value")
    return response

@app.get("/get-cookie/")
async def get_cookie(cookie_example: str = Cookie(None)):
    if cookie_example is None:
        raise HTTPException(status_code=400, detail="Cookie non trouvé")
    return {"message": f"La valeur du cookie est {cookie_example}"}    
    
    

    

"""
    @app.post("/page")
    def submit_formulaire(request:Request, username: str = Form(),password: str = Form()):
        
        query ="SELECT * FROM usernaoufel WHERE usernaoufel.username = %s"
        
        result =pd.read_sql_query(query, (username))
        print("Données récupérées de la base de données :", result)
        return templates.TemplateResponse(


  
    
    
@app.post("/page")
def submit_form(request: Request, username: str = Form(), password: str = Form()):
        
    with engine.connect() as connection:    
        query ="SELECT * FROM usernaoufel WHERE usernaoufel.username = username"
            
            
        result =connection.execute(query)
            
           
    return templates.TemplateResponse(request=request, name="page.html",context={"resultat":result})

                request=request, name="page.html")
"""
    
""" @app.get("/accueil")
def accueil(request:Request):
    with engine.begin() as connexion:
        query = text("SELECT tconst FROM castview LIMIT 10")
        resultat = (connexion.execute(query))
        rows = resultat.fetchall() 
            
        for row in rows:
            tconst = row[0]  # Accéder à l'élément 0 du tuple
            url = get_movie_poster_url(tconst)  # Appelle la fonction pour obtenir l'URL
            dico1[tconst] = url
            for cle, valeur in dico1.items():
                if valeur is None:
                    dico1[cle] = "https://www.proarti.fr/uploads/media/user/0001/22/thumb_21348_user_mini.gif"



   
    {%for x in dico1%}
    
        {% if dico == "None" %}
    
        {% else %}
        <div>{{dico1}}</div>
        {% endif %}
    {% endfor %}
    
    print(film,nbfilms)
    query = text('SELECT * from "castview" limit 1;')
    resultat = pd.read_sql_query(query,engine)
    
    recom = recommandation(resultat,film,nbfilms)
    print(resultat)
    
    for x in recom.resultat:
        tconst=x[0]
        url = get_movie_poster_url(tconst)  # Appelle la fonction pour obtenir l'URL
        dico2[tconst] = url
    for cle, valeur in dico2.items():
        if valeur is None:
            dico2[cle] = "https://img.freepik.com/vecteurs-premium/affiche-pour-film-bientot-disponible_664340-160.jpg"
    
"""
    
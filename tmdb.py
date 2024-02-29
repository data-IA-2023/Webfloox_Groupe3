import requests

# Fonction pour récupérer l'URL de la jaquette d'un film à partir de TMDb
def get_movie_poster_url(tmdb_id):
    api_key = '330f02856761de4af7dcfbad30b193ae'
    base_url = 'https://api.themoviedb.org/3/movie/'
    endpoint = f'{tmdb_id}?api_key={api_key}'
    response = requests.get(base_url + endpoint)
    if response.status_code == 200:
        data = response.json()
        if 'poster_path' in data:
            poster_path = data['poster_path']
            image=f'https://image.tmdb.org/t/p/w500/{poster_path}'
            synop=data['overview'] 
            return {'image': image , 'synop': synop}
    return {'image': "/static/image/nopicture.jpg" , 'synop': "Aucune description est disponible"}

def get_movie_synopsis(tmdb_id):
    api_key = '330f02856761de4af7dcfbad30b193ae'
    base_url = 'https://api.themoviedb.org/3/movie/'
    endpoint = f'{tmdb_id}?api_key={api_key}&language=fr'  # Ajoutez le paramètre 'language=fr' pour obtenir le synopsis en français
    response = requests.get(base_url + endpoint)
    if response.status_code == 200:
        data = response.json()
        if 'overview' in data:
            return data['overview']  # Récupérer le synopsis du film
    return None
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
            return f'https://image.tmdb.org/t/p/w500/{poster_path}'
    return None
import requests

# Fonction pour récupérer les info de la jaquette d'un film à partir de TMDb
def get_movie_poster_url(tmdb_id):
    api_key = '330f02856761de4af7dcfbad30b193ae'
    base_url = 'https://api.themoviedb.org/3/movie/'
    endpoint = f'{tmdb_id}?api_key={api_key}&append_to_response=videos'
    response = requests.get(base_url + endpoint)
    if response.status_code == 200:
        data = response.json()
        details = {'image': "/static/image/nopicture.jpg", 'synop': "Aucune description est disponible", 'video': None}

        if 'poster_path' in data:
            poster_path = data['poster_path']
            details['image'] = f'https://image.tmdb.org/t/p/w500/{poster_path}'

        if 'overview' in data:
            details['synop'] = data['overview']

        if 'videos' in data and 'results' in data['videos']:
            videos = data['videos']['results']
            for video in videos:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    details['video'] = f"https://www.youtube.com/embed/{video['key']}"
                    break

        return details

    return {'image': "/static/image/nopicture.jpg", 'synop': "Aucune description est disponible", 'video': ""}

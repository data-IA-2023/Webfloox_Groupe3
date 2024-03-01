import unittest
from tmdb import get_movie_poster_url

class TestMoviePosterUrl(unittest.TestCase):

    def test_get_movie_poster_url(self):
        tmdb_id = 'tt00000'
        expected_result = {'image': '/static/image/nopicture.jpg',
                           'synop': 'Aucune description est disponible', 
                           'video': ''}
        result = get_movie_poster_url(tmdb_id)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
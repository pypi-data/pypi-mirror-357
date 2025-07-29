import pandas as pd

from colab_filtering.norm.mean import mean_norm
from colab_filtering.similarity.cosine import cosine_similarity

ratings = [
    {'user_id': 1, 'movie': 'Matrix', 'rating': 5},
    {'user_id': 1, 'movie': 'Titanic', 'rating': 3},
    {'user_id': 1, 'movie': 'Inception', 'rating': 4},
    {'user_id': 2, 'movie': 'Matrix', 'rating': 4},
    {'user_id': 2, 'movie': 'Titanic', 'rating': 5},
    {'user_id': 2, 'movie': 'Inception', 'rating': 2},
    {'user_id': 2, 'movie': 'Avatar', 'rating': 3},
    {'user_id': 3, 'movie': 'Matrix', 'rating': 2},
    {'user_id': 3, 'movie': 'Titanic', 'rating': 2},
    {'user_id': 3, 'movie': 'Inception', 'rating': 5},
    {'user_id': 3, 'movie': 'Avatar', 'rating': 4},
    {'user_id': 4, 'movie': 'Matrix', 'rating': 5},
    {'user_id': 4, 'movie': 'Inception', 'rating': 4},
    {'user_id': 4, 'movie': 'Avatar', 'rating': 4},
    {'user_id': 4, 'movie': 'Interstellar', 'rating': 5},
    {'user_id': 5, 'movie': 'Titanic', 'rating': 4},
    {'user_id': 5, 'movie': 'Avatar', 'rating': 3},
    {'user_id': 5, 'movie': 'Interstellar', 'rating': 4},
]
df = pd.DataFrame(ratings)
utility = df.pivot_table(index='movie', columns='user_id', values='rating')

utility_norm = mean_norm(utility)
cosine_sim = cosine_similarity(utility_norm).round(3)


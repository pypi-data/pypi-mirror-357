# Colab-Filtering

A simple Python package for collaborative filtering in recommendation systems.

## Description

Colab-Filtering provides tools for implementing collaborative filtering techniques in recommendation systems. It includes functions for data normalization and similarity calculations, which are essential components in building recommendation engines.

## Features

- **Normalization**: Mean-centering of utility matrices
- **Similarity Metrics**: 
  - Cosine similarity for numeric ratings
  - Jaccard similarity for binary data

## Installation

```bash
pip install colab_filtering
```

## Requirements

- Python >= 3.12
- pandas >= 2.3.0

## Usage

### Basic Example

```python
import pandas as pd
from norm.mean import mean_norm
from similarity.cosine import cosine_similarity

# Create a utility matrix (users x items)
ratings = [
    {'user_id': 1, 'movie': 'Matrix', 'rating': 5},
    {'user_id': 1, 'movie': 'Titanic', 'rating': 3},
    # ... more ratings
]
df = pd.DataFrame(ratings)
utility = df.pivot_table(index='movie', columns='user_id', values='rating')

# Apply mean normalization
utility_norm = mean_norm(utility)

# Calculate cosine similarity between items
cosine_sim = cosine_similarity(utility_norm)
```

### Using Jaccard Similarity for Binary Data

```python
import pandas as pd
from similarity.jaccard import jaccard_similarity

# Create a binary utility matrix (1 for rated, 0 for not rated)
binary_utility = utility.notna().astype(int)

# Calculate Jaccard similarity
jaccard_sim = jaccard_similarity(binary_utility)
```

## Module Descriptions

### norm

- **mean.py**: Provides functions for mean normalization of utility matrices.

### similarity

- **cosine.py**: Implements cosine similarity calculations between users or items.
- **jaccard.py**: Implements Jaccard similarity calculations, useful for binary data.

## Author

- Henning Schmies (henning.schmies@stud.th-deg.de)

## License

This project is licensed under the terms specified in the LICENSE.txt file.

## Keywords

big data, collaborative filtering, recommendation, filtering
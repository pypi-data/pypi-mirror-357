import numpy as np
import pandas as pd


def cosine_similarity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the cosine similarity between all pairs of rows in a DataFrame.

    Cosine similarity measures the cosine of the angle between two vectors, providing
    a similarity score between -1 and 1. In the context of collaborative filtering,
    it's used to find similar users or items based on their rating patterns.

    Args:
        df (pd.DataFrame): The input DataFrame where rows represent users or items,
                          columns represent items or users, and values represent ratings.
                          Missing values (NaN) are handled appropriately.

    Returns:
        pd.DataFrame: A square DataFrame with the same index as the input DataFrame,
                     containing the cosine similarity between each pair of rows.
                     If two rows have no overlapping non-NaN values, their similarity
                     will be NaN.

    Example:
        >>> import pandas as pd
        >>> data = {'item1': [5, 3, np.nan], 'item2': [4, np.nan, 2]}
        >>> df = pd.DataFrame(data, index=['user1', 'user2', 'user3'])
        >>> cosine_similarity(df)
                user1      user2      user3
        user1  1.000000       NaN       NaN
        user2       NaN  1.000000       NaN
        user3       NaN       NaN  1.000000
    """
    users = df.index
    sims = pd.DataFrame(index=users, columns=users, dtype=float)

    for u in users:
        for v in users:
            both_rated = df.loc[u].notna() & df.loc[v].notna()
            if not both_rated.any():
                sims.loc[u, v] = np.nan
                continue

            vec_u = df.loc[u, both_rated].to_numpy(dtype=float)
            vec_v = df.loc[v, both_rated].to_numpy(dtype=float)

            dot = np.dot(vec_u, vec_v)
            norm = np.linalg.norm(vec_u) * np.linalg.norm(vec_v)
            sims.loc[u, v] = dot / norm if norm else np.nan

    return sims

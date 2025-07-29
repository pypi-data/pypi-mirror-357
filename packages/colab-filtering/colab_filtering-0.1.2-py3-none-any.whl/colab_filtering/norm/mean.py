import pandas as pd


def mean_norm(u: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a utility matrix by subtracting the mean of each row.

    This function performs mean-centering normalization on a utility matrix,
    which is a common preprocessing step in collaborative filtering. It helps
    address user rating biases by centering each user's ratings around zero.

    Args:
        u (pd.DataFrame): The utility matrix to normalize. Typically, rows represent
                         items or users, and columns represent users or items.
                         The values are ratings or preferences.

    Returns:
        pd.DataFrame: A normalized version of the input matrix with the same shape,
                     where each row's values are centered around zero.

    Example:
        >>> import pandas as pd
        >>> data = {'user1': [5, 3, 4], 'user2': [4, 5, 2]}
        >>> df = pd.DataFrame(data, index=['movie1', 'movie2', 'movie3'])
        >>> mean_norm(df)
           user1  user2
        movie1  1.0   0.0
        movie2 -1.0   1.0
        movie3  0.0  -2.0
    """
    means = u.mean(axis=1, skipna=True)
    centered = u.sub(means, axis=0)
    return centered

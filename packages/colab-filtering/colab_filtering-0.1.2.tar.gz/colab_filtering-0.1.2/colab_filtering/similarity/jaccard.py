import numpy as np
import pandas as pd


def jaccard_similarity(df_binary: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the Jaccard similarity between all pairs of rows in a binary DataFrame.

    Jaccard similarity is defined as the size of the intersection divided by the size
    of the union of two sets. In the context of collaborative filtering, it's often used
    to measure similarity between users or items based on binary attributes (e.g., whether
    a user has rated an item, regardless of the rating value).

    Args:
        df_binary (pd.DataFrame): A binary DataFrame where rows represent users or items,
                                 columns represent items or users, and values are binary
                                 (typically 0 or 1, True or False).

    Returns:
        pd.DataFrame: A square DataFrame with the same index as the input DataFrame,
                     containing the Jaccard similarity between each pair of rows.
                     Values range from 0 (no similarity) to 1 (identical).
                     If two rows have no 1's (or True values), their similarity will be NaN.

    Example:
        >>> import pandas as pd
        >>> data = {'item1': [1, 1, 0], 'item2': [1, 0, 1], 'item3': [0, 1, 1]}
        >>> df = pd.DataFrame(data, index=['user1', 'user2', 'user3'])
        >>> jaccard_similarity(df)
                user1      user2      user3
        user1  1.000000  0.333333  0.333333
        user2  0.333333  1.000000  0.333333
        user3  0.333333  0.333333  1.000000
    """
    users = df_binary.index
    J = pd.DataFrame(index=users, columns=users, dtype=float)
    for u in users:
        for v in users:
            inter = np.logical_and(df_binary.loc[u], df_binary.loc[v]).sum()
            union = np.logical_or(df_binary.loc[u], df_binary.loc[v]).sum()
            J.loc[u, v] = inter / union if union else np.nan
    return J

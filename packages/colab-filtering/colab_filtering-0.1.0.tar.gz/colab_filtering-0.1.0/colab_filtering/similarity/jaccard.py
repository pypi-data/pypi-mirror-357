import numpy as np
import pandas as pd


def jaccard_similarity(df_binary: pd.DataFrame):
    users = df_binary.index
    J = pd.DataFrame(index=users, columns=users, dtype=float)
    for u in users:
        for v in users:
            inter = np.logical_and(df_binary.loc[u], df_binary.loc[v]).sum()
            union = np.logical_or(df_binary.loc[u], df_binary.loc[v]).sum()
            J.loc[u, v] = inter / union if union else np.nan
    return J

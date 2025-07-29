import numpy as np
import pandas as pd


def cosine_similarity(df: pd.DataFrame) -> pd.DataFrame:
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

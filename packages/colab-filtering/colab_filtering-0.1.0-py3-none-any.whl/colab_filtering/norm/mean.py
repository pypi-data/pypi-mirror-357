import pandas as pd


def mean_norm(u: pd.DataFrame) -> pd.DataFrame:
    means = u.mean(axis=1, skipna=True)
    centered = u.sub(means, axis=0)
    return centered

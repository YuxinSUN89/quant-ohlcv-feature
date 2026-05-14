import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Psy
    df = df.with_columns(pl.Series("P", np.where(df["close"] > df["close"].shift(1), 1, 0)).fill_nan(None))
    df = df.with_columns(pl.Series(factor_name, df["P"].rolling_sum(n, min_samples=config.min_periods) / n * 100))

    # delete extra columns
    df = df.drop("P")

    return df

import polars as pl

from impl_polars.helpers import rolling_corr_np


def signal(df, n, factor_name, config):
    # Return Autocorrelation (lag-1 rolling autocorrelation of returns)
    # Formula: RETURN = (CLOSE - CLOSE.shift(1)) / CLOSE.shift(1)
    #          result = ROLLING_CORR(RETURN, RETURN.shift(1), N)
    # Measures the persistence of returns over the past N periods.
    # Positive values indicate momentum (trending), negative values indicate mean-reversion.
    df = df.with_columns(pl.Series("_return", df["close"].pct_change()))
    df = df.with_columns(pl.Series("_return_lag1", df["_return"].shift(1)))

    df = df.with_columns(pl.Series(factor_name, rolling_corr_np(df["_return"], df["_return_lag1"], n, 2, config)))

    df = df.drop("_return")
    df = df.drop("_return_lag1")

    return df

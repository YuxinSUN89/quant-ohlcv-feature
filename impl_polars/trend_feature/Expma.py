import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** Expma ********************
    # N1=12
    # N2=50
    # EMA1=EMA(CLOSE,N1)
    # EMA2=EMA(CLOSE,N2)
    # Exponential Moving Average is an improved version of the Simple Moving Average, designed to reduce the lag problem.
    ema1 = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    ema2 = df["close"].ewm_mean(span=4 * n, adjust=config.ewm_adjust)

    s = ema1 - ema2
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

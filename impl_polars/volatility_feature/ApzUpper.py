import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # ApzUpper indicator
    """
    N=10
    M=20
    PARAM=2
    VOL=EMA(EMA(HIGH-LOW,N),N)
    UPPER=EMA(EMA(CLOSE,M),M)+PARAM*VOL
    LOWER= EMA(EMA(CLOSE,M),M)-PARAM*VOL
    ApzUpper (Adaptive Price Zone) is similar to Bollinger Bands and the Keltner Channel:
    all are price channels built around a moving average based on price volatility.
    The difference lies in how volatility is measured: Bollinger Bands use the standard
    deviation of the close, the Keltner Channel uses the true range ATR, and ApzUpper uses
    the N-day double exponential average of the high-low difference to measure price amplitude.
    """
    vol = (df["high"] - df["low"]).ewm_mean(span=n, adjust=config.ewm_adjust).ewm_mean(span=n, adjust=config.ewm_adjust)
    upper = (
        df["close"]
        .ewm_mean(span=int(2 * n), adjust=config.ewm_adjust)
        .ewm_mean(span=int(2 * n), adjust=config.ewm_adjust)
        + 2 * vol
    )

    s = upper
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

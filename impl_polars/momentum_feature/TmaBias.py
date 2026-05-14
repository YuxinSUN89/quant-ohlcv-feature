import polars as pl


def signal(df, n, factor_name, config):
    # TmaBias
    eps = config.eps
    """
    N=20
    CLOSE_MA=MA(CLOSE,N)
    TMA=MA(CLOSE_MA,N)
    TMA is similar to other moving averages, but unlike EMA which gives more weight to prices
    closer to the current day, TMA gives more weight to prices in the middle of the considered
    time window. Buy/sell signals are generated when price crosses above/below TMA.
    """
    ma = df["close"].rolling_mean(n, min_samples=config.min_periods)  # CLOSE_MA=MA(CLOSE,N)
    tma = ma.rolling_mean(n, min_samples=config.min_periods)  # TMA=MA(CLOSE_MA,N)
    df = df.with_columns(pl.Series(factor_name, df["close"] / (tma + eps) - 1))

    return df

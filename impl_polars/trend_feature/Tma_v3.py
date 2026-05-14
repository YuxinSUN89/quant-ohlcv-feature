import polars as pl


def signal(df, n, factor_name, config):
    # TMA indicator
    """
    N=20
    CLOSE_MA=MA(CLOSE,N)
    TMA=MA(CLOSE_MA,N)
    TMA is similar to other moving averages, but unlike EMA which gives more weight to prices
    closer to the current day, TMA gives more weight to prices in the middle of the considered
    time window. Buy/sell signals are generated when price crosses above/below TMA.
    """
    _ts = (
        df["high"].rolling_max(n, min_samples=config.min_periods)
        + df["low"].rolling_min(n, min_samples=config.min_periods)
    ) / 2.0

    close_ma = _ts.rolling_mean(n, min_samples=config.min_periods)
    tma = close_ma.rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, df["close"] / tma - 1))

    return df

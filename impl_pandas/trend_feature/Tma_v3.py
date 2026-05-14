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
        df["high"].rolling(n, min_periods=config.min_periods).max()
        + df["low"].rolling(n, min_periods=config.min_periods).min()
    ) / 2.0

    close_ma = _ts.rolling(n, min_periods=config.min_periods).mean()
    tma = close_ma.rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["close"] / tma - 1

    return df

def signal(df, n, factor_name, config):
    # calculate macd indicator
    """
    N1=20
    N2=40
    N3=5
    MACD=EMA(CLOSE,N1)-EMA(CLOSE,N2)
    MACD_SIGNAL=EMA(MACD,N3)
    MACD_HISTOGRAM=MACD-MACD_SIGNAL
    The MACD indicator measures the difference between the fast and slow moving averages.
    Since the slow MA reflects price direction over a longer previous period and the fast MA
    reflects a shorter period, the fast MA rises faster than the slow MA in an uptrend and
    falls faster in a downtrend. Therefore, MACD crossing above/below 0 can be used as a
    trading signal. Another approach is to compute the difference between MACD and its
    moving average (signal line) to get the MACD histogram, and use histogram crossings
    above/below 0 (i.e., MACD crossing its signal line) to generate signals. This method
    can also be applied to other indicators.
    """
    short_windows = n
    long_windows = 3 * n
    macd_windows = int(1.618 * n)

    df["ema_short"] = df["close"].ewm(span=short_windows, adjust=config.ewm_adjust).mean()
    df["ema_long"] = df["close"].ewm(span=long_windows, adjust=config.ewm_adjust).mean()
    df["dif"] = df["ema_short"] - df["ema_long"]
    df["dea"] = df["dif"].ewm(span=macd_windows, adjust=config.ewm_adjust).mean()
    df["macd"] = 2 * (df["dif"] - df["dea"])

    df[factor_name] = df["macd"] / df["macd"].rolling(macd_windows, min_periods=config.min_periods).mean() - 1

    del df["ema_short"]
    del df["ema_long"]
    del df["dif"]
    del df["dea"]
    del df["macd"]

    return df

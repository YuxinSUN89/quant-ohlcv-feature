import polars as pl


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

    df = df.with_columns(pl.Series("ema_short", df["close"].ewm_mean(span=short_windows, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_long", df["close"].ewm_mean(span=long_windows, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("dif", df["ema_short"] - df["ema_long"]))
    df = df.with_columns(pl.Series("dea", df["dif"].ewm_mean(span=macd_windows, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("macd", 2 * (df["dif"] - df["dea"])))

    df = df.with_columns(
        pl.Series(factor_name, df["macd"] / df["macd"].rolling_mean(macd_windows, min_samples=config.min_periods) - 1)
    )

    df = df.drop("ema_short")
    df = df.drop("ema_long")
    df = df.drop("dif")
    df = df.drop("dea")
    df = df.drop("macd")

    return df

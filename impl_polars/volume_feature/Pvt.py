import polars as pl


def signal(df, n, factor_name, config):
    # Pvt indicator
    eps = config.eps
    """
    PVT=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*VOLUME
    PVT_MA1=MA(PVT,N1)
    PVT_MA2=MA(PVT,N2)
    PVT uses the rate of price change as a weight to compute a moving average of volume.
    PVT is conceptually similar to OBV, but unlike OBV (which only considers price direction),
    PVT accounts for the magnitude of price changes.
    Here we use crossings of short and long PVT moving averages to generate signals.
    A buy signal is generated when PVT_MA1 crosses above PVT_MA2;
    a sell signal is generated when PVT_MA1 crosses below PVT_MA2.
    """

    df = df.with_columns(pl.Series("PVT", (df["close"] - df["close"].shift(1)) / (df["close"].shift(1) + config.eps) * df["volume"]))
    df = df.with_columns(pl.Series("PVT_MA", df["PVT"].rolling_mean(n, min_samples=config.min_periods)))

    # normalize
    df = df.with_columns(pl.Series("PVT_SIGNAL", (df["PVT"] / (df["PVT_MA"] + eps) - 1)))
    df = df.with_columns(pl.Series(factor_name, df["PVT_SIGNAL"].rolling_sum(n, min_samples=config.min_periods)))

    # remove redundant columns
    df = df.drop(["PVT", "PVT_MA", "PVT_SIGNAL"])

    return df

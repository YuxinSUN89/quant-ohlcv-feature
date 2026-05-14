import polars as pl


def signal(df, n, factor_name, config):
    # PVT indicator
    """
    PVT=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*VOLUME
    PVT_MA1=MA(PVT,N1)
    PVT_MA2=MA(PVT,N2)
    PVT uses the rate of price change as a weight to compute a moving average of volume.
    PVT is conceptually similar to OBV, but unlike OBV (which only considers price direction),
    PVT accounts for the magnitude of price changes. Here we use crossings of short and long
    PVT moving averages to generate signals.
    A buy signal is generated when PVT_MA1 crosses above PVT_MA2;
    a sell signal is generated when PVT_MA1 crosses below PVT_MA2.
    """
    df = df.with_columns(pl.Series("PVT", (df["close"] - df["close"].shift(1)) / (df["close"].shift(1) + config.eps) * df["volume"]))
    df = df.with_columns(pl.Series("PVT_MA1", df["PVT"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("PVT_MA2", df["PVT"].rolling_mean(2 * n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("Pvt_v2", df["PVT_MA1"] - df["PVT_MA2"]))

    # normalize
    df = df.with_columns(pl.Series(factor_name, df["PVT"] / df["Pvt_v2"] - 1))

    return df

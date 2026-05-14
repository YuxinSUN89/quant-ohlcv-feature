import polars as pl


def signal(df, n, factor_name, config):
    # Pvt_v2 indicator
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

    df = df.with_columns(pl.Series("PVT", df["close"].pct_change() * df["volume"]))
    # normalize

    df = df.with_columns(
        pl.Series("PVT_score", (df["PVT"] - df["PVT"].rolling_mean(n, min_samples=config.min_periods)))
        / (df["PVT"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof) + eps)
    )
    df = df.with_columns(pl.Series(factor_name, df["PVT_score"].rolling_sum(n, min_samples=config.min_periods)))

    # remove irrelevant columns
    df = df.drop(["PVT", "PVT_score"])

    return df

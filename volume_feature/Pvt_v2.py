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

    df["PVT"] = df["close"].pct_change() * df["volume"]
    # normalize

    df["PVT_score"] = (df["PVT"] - df["PVT"].rolling(n, min_periods=config.min_periods).mean()) / (
        df["PVT"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof) + eps
    )
    df[factor_name] = df["PVT_score"].rolling(n, min_periods=config.min_periods).sum()

    # remove irrelevant columns
    del df["PVT"], df["PVT_score"]

    return df

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

    df["PVT"] = (df["close"] - df["close"].shift(1)) / df["close"].shift(1) * df["volume"]
    df["PVT_MA"] = df["PVT"].rolling(n, min_periods=config.min_periods).mean()

    # normalize
    df["PVT_SIGNAL"] = df["PVT"] / (df["PVT_MA"] + eps) - 1
    df[factor_name] = df["PVT_SIGNAL"].rolling(n, min_periods=config.min_periods).sum()

    # remove redundant columns
    del df["PVT"], df["PVT_MA"], df["PVT_SIGNAL"]

    return df

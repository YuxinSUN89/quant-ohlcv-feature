def signal(df, n, factor_name, config):
    # Pac indicator
    eps = config.eps
    """
    N1=20
    N2=20
    UPPER=SMA(HIGH,N1,1)
    LOWER=SMA(LOW,N2,1)
    Construct a price channel using moving averages of high and low prices.
    Go long if price breaks above the upper band; go short if it breaks below the lower band.
    """
    df["upper"] = df["high"].ewm(span=n, adjust=config.ewm_adjust).mean()  # UPPER=SMA(HIGH,N1,1)
    df["lower"] = df["low"].ewm(span=n, adjust=config.ewm_adjust).mean()  # LOWER=SMA(LOW,N2,1)
    df["width"] = df["upper"] - df["lower"]  # add indicator to compute width for normalization
    df["width_ma"] = df["width"].rolling(n, min_periods=config.min_periods).mean()

    df[factor_name] = df["width"] / (df["width_ma"] + eps) - 1

    # remove redundant columns
    del df["upper"], df["lower"], df["width"], df["width_ma"]

    return df

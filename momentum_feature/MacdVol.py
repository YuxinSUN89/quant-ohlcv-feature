def signal(df, n, factor_name, config):
    # MACDVOL indicator
    """
    N1=20
    N2=40
    N3=10
    MACDVOL=EMA(VOLUME,N1)-EMA(VOLUME,N2)
    SIGNAL=MA(MACDVOL,N3)
    MACDVOL is the volume version of MACD. Buy when MACDVOL crosses above SIGNAL;
    sell when it crosses below SIGNAL.
    """
    N1 = 2 * n
    N2 = 4 * n
    N3 = n
    df["ema_volume_1"] = df["volume"].ewm(span=N1, adjust=config.ewm_adjust).mean()
    df["ema_volume_2"] = df["volume"].ewm(span=N2, adjust=config.ewm_adjust).mean()
    df["MACDV"] = df["ema_volume_1"] - df["ema_volume_2"]
    df["SIGNAL"] = df["MACDV"].rolling(N3, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = df["MACDV"] / df["SIGNAL"] - 1

    del df["ema_volume_1"]
    del df["ema_volume_2"]
    del df["MACDV"]
    del df["SIGNAL"]

    return df

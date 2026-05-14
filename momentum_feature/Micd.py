def signal(df, n, factor_name, config):
    # MICD indicator
    """
    N=20
    N1=10
    N2=20
    M=10
    MI=CLOSE-REF(CLOSE,1)
    MTMMA=SMA(MI,N,1)
    DIF=MA(REF(MTMMA,1),N1)-MA(REF(MTMMA,1),N2)
    MICD=SMA(DIF,M,1)
    A buy signal is generated when MICD crosses above 0;
    a sell signal is generated when MICD crosses below 0.
    """
    df["MI"] = df["close"] - df["close"].shift(1)
    df["MIMMA"] = df["MI"].rolling(n, min_periods=config.min_periods).mean()
    df["MIMMA_MA1"] = df["MIMMA"].shift(1).rolling(n, min_periods=config.min_periods).mean()
    df["MIMMA_MA2"] = df["MIMMA"].shift(1).rolling(2 * n, min_periods=config.min_periods).mean()
    df["DIF"] = df["MIMMA_MA1"] - df["MIMMA_MA2"]
    df["MICD"] = df["DIF"].rolling(n, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = df["DIF"] / df["MICD"]

    del df["MI"]
    del df["MIMMA"]
    del df["MIMMA_MA1"]
    del df["MIMMA_MA2"]
    del df["DIF"]
    del df["MICD"]

    return df

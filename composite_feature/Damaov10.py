def signal(df, n, factor_name, config):
    # Damaov10 indicator (COPP × BBW × ATR composite)
    # Formula: COPP = MA(100*((CLOSE-REF(CLOSE,N))/REF(CLOSE,N) + (CLOSE-REF(CLOSE,2N))/REF(CLOSE,2N)), N)
    #          BBW = STD * MA(|CLOSE-MA|/STD, N) * 2 / MA(CLOSE,N)  (volatility-weighted Bollinger width)
    #          ATR = MA(TR,N) / MA(CLOSE,N)  (normalized ATR)
    #          result = COPP * BBW_mean * ATR
    # Combines momentum (COPP), Bollinger volatility (BBW), and range volatility (ATR) into one composite signal.
    eps = config.eps
    # COPP
    # RC=100*((CLOSE-REF(CLOSE,N1))/REF(CLOSE,N1)+(CLOSE-REF(CLOSE,N2))/REF(CLOSE,N2))
    df["RC"] = 100 * (
        (df["close"] - df["close"].shift(n)) / df["close"].shift(n)
        + (df["close"] - df["close"].shift(2 * n)) / df["close"].shift(2 * n)
    )
    df["RC_mean"] = df["RC"].rolling(n, min_periods=config.min_periods).mean()
    # BBW
    df["median"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["z_score"] = abs(df["close"] - df["median"]) / df["std"]
    df["m"] = df["z_score"].rolling(window=n, min_periods=config.min_periods).mean()
    df["BBW"] = df["std"] * df["m"] * 2 / (df["median"] + eps)
    df["BBW_mean"] = df["BBW"].rolling(n, min_periods=config.min_periods).mean()
    # ATR
    df["c1"] = df["high"] - df["low"]  # HIGH-LOW
    df["c2"] = abs(df["high"] - df["close"].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df["c3"] = abs(df["low"] - df["close"].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)  # TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    df["_ATR"] = df["TR"].rolling(n, min_periods=config.min_periods).mean()  # ATR=MA(TR,N)
    # normalize ATR indicator
    df["ATR"] = df["_ATR"] / df["median"]

    df[factor_name] = df["RC_mean"] * df["BBW_mean"] * df["ATR"]
    # delete extra columns
    del df["RC"], df["RC_mean"], df["median"]
    del df["std"], df["z_score"], df["m"]
    del df["BBW"], df["BBW_mean"], df["c1"]
    del df["c2"], df["c3"], df["TR"], df["_ATR"]
    del df["ATR"]

    return df

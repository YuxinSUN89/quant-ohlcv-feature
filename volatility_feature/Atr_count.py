def signal(df, n, factor_name, config):
    """
    N=20
    TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    ATR=MA(TR,N)
    MIDDLE=MA(CLOSE,N)
    """
    df["c1"] = df["high"] - df["low"]  # HIGH-LOW
    df["c2"] = abs(df["high"] - df["close"].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df["c3"] = abs(df["low"] - df["close"].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)  # TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    df["_ATR"] = df["TR"].rolling(n, min_periods=config.min_periods).mean()  # ATR=MA(TR,N)
    df["middle"] = df["close"].rolling(n, min_periods=config.min_periods).mean()  # MIDDLE=MA(CLOSE,N)
    df["upper"] = df["middle"] + 2 * df["_ATR"]
    df["lower"] = df["middle"] - 2 * df["_ATR"]

    df["count"] = 0
    df.loc[df["close"] > df["upper"], "count"] = 1
    df.loc[df["close"] < df["lower"], "count"] = -1
    df[factor_name] = df["count"].rolling(n, min_periods=config.min_periods).sum()
    # del df['mean']
    # del df['std']
    del df["upper"]
    del df["lower"]
    del df["count"]
    del df["c1"]
    del df["c2"]
    del df["c3"]
    del df["TR"]
    del df["_ATR"]
    del df["middle"]

    return df

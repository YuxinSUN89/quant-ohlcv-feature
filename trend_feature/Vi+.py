def signal(df, n, factor_name, config):
    # VI indicator
    """
    TR=MAX([ABS(HIGH-LOW),ABS(LOW-REF(CLOSE,1)),ABS(HIG
    H-REF(CLOSE,1))])
    VMPOS=ABS(HIGH-REF(LOW,1))
    VMNEG=ABS(LOW-REF(HIGH,1))
    N=40
    SUMPOS=SUM(VMPOS,N)
    SUMNEG=SUM(VMNEG,N)
    TRSUM=SUM(TR,N)
    VI+=SUMPOS/TRSUM
    VI-=SUMNEG/TRSUM
    VI can be seen as a variant of ADX. VI+ and VI- in the VI indicator are similar to
    DI+ and DI- in ADX. The difference is that ADX uses the differences between current and
    previous high prices and between current and previous low prices to measure price change,
    while VI uses the differences between current high and previous low, and current low and
    previous high. When VI+ crosses above/below VI-, the bull/bear signal strengthens, generating buy/sell signals.
    """
    df["c1"] = abs(df["high"] - df["low"])
    df["c2"] = abs(df["close"] - df["close"].shift(1))
    df["c3"] = abs(df["high"] - df["close"].shift(1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)

    df["VMPOS"] = abs(df["high"] - df["low"].shift(1))
    df["VMNEG"] = abs(df["low"] - df["high"].shift(1))
    df["sum_pos"] = df["VMPOS"].rolling(n, min_periods=config.min_periods).sum()
    df["sum_neg"] = df["VMNEG"].rolling(n, min_periods=config.min_periods).sum()

    df["sum_tr"] = df["TR"].rolling(n, min_periods=config.min_periods).sum()
    df[factor_name] = df["sum_pos"] / df["sum_tr"]  # Vi+
    # df['VI-'] = df['sum_neg'] / df['sum_tr'] #Vi-

    del df["c1"]
    del df["c2"]
    del df["c3"]
    del df["TR"]
    del df["VMPOS"]
    del df["VMNEG"]
    del df["sum_pos"]
    del df["sum_neg"]
    del df["sum_tr"]

    return df

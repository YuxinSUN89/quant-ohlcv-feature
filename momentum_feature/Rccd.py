def signal(df, n, factor_name, config):
    # RCCD indicator
    """
    M=40
    N1=20
    N2=40
    RC=CLOSE/REF(CLOSE,M)
    ARC1=SMA(REF(RC,1),M,1)
    DIF=MA(REF(ARC1,1),N1)-MA(REF(ARC1,1),N2)
    RCCD=SMA(DIF,M,1)
    RC is the ratio of the current price to the previous day's price. When RC > 1, prices are rising;
    when RC increases, the rate of price increase is accelerating. When RC < 1, prices are falling;
    when RC decreases, the rate of decline is accelerating. RCCD first smooths the RC indicator,
    then takes the difference between moving averages of different time lengths, then takes another
    moving average. Buy/sell signals are generated when RCCD crosses above/below 0.
    """
    df["RC"] = df["close"] / df["close"].shift(2 * n)
    df["ARC1"] = df["RC"].rolling(2 * n, min_periods=config.min_periods).mean()
    df["MA1"] = df["ARC1"].shift(1).rolling(n, min_periods=config.min_periods).mean()
    df["MA2"] = df["ARC1"].shift(1).rolling(2 * n, min_periods=config.min_periods).mean()
    df["DIF"] = df["MA1"] - df["MA2"]
    df[factor_name] = df["DIF"].rolling(2 * n, min_periods=config.min_periods).mean()

    del df["RC"]
    del df["ARC1"]
    del df["MA1"]
    del df["MA2"]
    del df["DIF"]

    return df

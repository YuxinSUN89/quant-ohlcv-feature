def signal(df, n, factor_name, config):
    # CCI - most commonly used T indicator
    eps = config.eps
    """
    N=14
    TP=(HIGH+LOW+CLOSE)/3
    MA=MA(TP,N)
    MD=MA(ABS(TP-MA),N)
    CCI=(TP-MA)/(0.015MD)
    The CCI indicator measures the deviation of the typical price (mean of high, low, and close) from its moving average over a period.
    CCI can be used to reflect overbought and oversold market conditions.
    Generally, CCI above 100 indicates the market is overbought; CCI below -100 indicates the market is oversold.
    When CCI crosses below 100 / crosses above -100, it suggests the price may begin to reverse, and one may consider selling/buying.
    """

    df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
    df["ma"] = df["tp"].rolling(window=n, min_periods=config.min_periods).mean()
    df["md"] = abs(df["tp"] - df["ma"]).rolling(window=n, min_periods=config.min_periods).mean()

    df[factor_name] = (df["tp"] - df["ma"]) / (df["md"] * 0.015 + eps)

    del df["tp"]
    del df["ma"]
    del df["md"]

    return df

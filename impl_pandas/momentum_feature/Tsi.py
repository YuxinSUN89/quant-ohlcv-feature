def signal(df, n, factor_name, config):
    # TSI indicator
    """
    N1=25
    N2=13
    TSI=EMA(EMA(CLOSE-REF(CLOSE,1),N1),N2)/EMA(EMA(ABS(
    CLOSE-REF(CLOSE,1)),N1),N2)*100
    TSI is a double moving average indicator. Unlike the common moving average indicator which takes the moving average of the close price,
    TSI takes the moving average of the difference between two days' close prices. If TSI crosses above 10 /
    crosses below -10, it generates a buy/sell signal.
    """
    n1 = 2 * n
    df["diff_close"] = df["close"] - df["close"].shift(1)
    df["ema"] = df["diff_close"].ewm(span=n1, adjust=config.ewm_adjust).mean()
    df["ema_ema"] = df["ema"].ewm(span=n, adjust=config.ewm_adjust).mean()

    df["abs_diff_close"] = abs(df["diff_close"])
    df["abs_ema"] = df["abs_diff_close"].ewm(span=n1, adjust=config.ewm_adjust).mean()
    df["abs_ema_ema"] = df["abs_ema"].ewm(span=n, adjust=config.ewm_adjust).mean()

    df[factor_name] = df["ema_ema"] / df["abs_ema_ema"] * 100

    del df["diff_close"]
    del df["ema"]
    del df["ema_ema"]
    del df["abs_diff_close"]
    del df["abs_ema"]
    del df["abs_ema_ema"]

    return df

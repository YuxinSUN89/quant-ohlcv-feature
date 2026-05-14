def signal(df, n, factor_name, config):
    """
    AdaptBollingv3
    Use the mtm_mean from the original v3 timing strategy as the factor B selector.
    """
    n1 = int(n)

    # ==============================================================

    df["mtm"] = df["close"] / df["close"].shift(n1) - 1
    df["mtm_mean"] = df["mtm"].rolling(window=n1, min_periods=config.min_periods).mean()

    # calculate volatility factor wd_atr based on price ATR
    df["c1"] = df["high"] - df["low"]
    df["c2"] = abs(df["high"] - df["close"].shift(1))
    df["c3"] = abs(df["low"] - df["close"].shift(1))
    df["tr"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["atr"] = df["tr"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["avg_price_"] = df["close"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["wd_atr"] = df["atr"] / df["avg_price_"]

    # reference ATR to calculate volatility factor for MTM indicator
    df["mtm_l"] = df["low"] / df["low"].shift(n1) - 1
    df["mtm_h"] = df["high"] / df["high"].shift(n1) - 1
    df["mtm_c"] = df["close"] / df["close"].shift(n1) - 1
    df["mtm_c1"] = df["mtm_h"] - df["mtm_l"]
    df["mtm_c2"] = abs(df["mtm_h"] - df["mtm_c"].shift(1))
    df["mtm_c3"] = abs(df["mtm_l"] - df["mtm_c"].shift(1))
    df["mtm_tr"] = df[["mtm_c1", "mtm_c2", "mtm_c3"]].max(axis=1)
    df["mtm_atr"] = df["mtm_tr"].rolling(window=n1, min_periods=config.min_periods).mean()

    # reference ATR to calculate volatility factor for MTM mean indicator
    df["mtm_l_mean"] = df["mtm_l"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["mtm_h_mean"] = df["mtm_h"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["mtm_c_mean"] = df["mtm_c"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["mtm_c1"] = df["mtm_h_mean"] - df["mtm_l_mean"]
    df["mtm_c2"] = abs(df["mtm_h_mean"] - df["mtm_c_mean"].shift(1))
    df["mtm_c3"] = abs(df["mtm_l_mean"] - df["mtm_c_mean"].shift(1))
    df["mtm_tr"] = df[["mtm_c1", "mtm_c2", "mtm_c3"]].max(axis=1)
    df["mtm_atr_mean"] = df["mtm_tr"].rolling(window=n1, min_periods=config.min_periods).mean()

    indicator = "mtm_mean"

    # multiply mtm_mean indicator by three volatility factors
    df[indicator] = df[indicator] * df["mtm_atr"]
    df[indicator] = df[indicator] * df["mtm_atr_mean"]
    df[indicator] = df[indicator] * df["wd_atr"]

    df[factor_name] = df[indicator] * 100000000

    drop_col = [
        "mtm",
        "mtm_mean",
        "c1",
        "c2",
        "c3",
        "tr",
        "atr",
        "wd_atr",
        "mtm_l",
        "mtm_h",
        "mtm_c",
        "mtm_c1",
        "mtm_c2",
        "mtm_c3",
        "mtm_tr",
        "mtm_atr",
        "mtm_l_mean",
        "mtm_h_mean",
        "mtm_c_mean",
        "mtm_atr_mean",
        "avg_price_",
    ]
    df.drop(columns=drop_col, inplace=True)

    return df

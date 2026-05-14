def signal(df, n, factor_name, config):
    """
    Build using hint as the B-selection factor
    """
    # ==============================================================

    df["mtm"] = df["high"] / df["high"].shift(n) - 1
    df["mtm_mean"] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean()
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["cm"] = df["close"] / df["ma"]
    df[factor_name] = (df["mtm_mean"] - df["cm"]) / df["cm"]

    return df

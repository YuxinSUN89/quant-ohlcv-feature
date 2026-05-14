def signal(df, n, factor_name, config):
    # MagicCci indicator (CCI using OHLC average as typical price, EWM-based)
    # Formula: TP = (EMA(O,N) + EMA(H,N) + EMA(L,N) + EMA(C,N)) / 4
    #          MA = EMA(TP, N); MD = EMA(|TP - MA|, N)
    #          result = (TP - MA) / (MD + eps)
    # Uses all four OHLC prices EWM-smoothed to compute a robust CCI variant.
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
    eps = config.eps
    df["oma"] = df["open"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["hma"] = df["high"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["lma"] = df["low"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["cma"] = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["tp"] = (df["oma"] + df["hma"] + df["lma"] + df["cma"]) / 4
    df["ma"] = df["tp"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["abs_diff_close"] = abs(df["tp"] - df["ma"])
    df["md"] = df["abs_diff_close"].ewm(span=n, adjust=config.ewm_adjust).mean()

    df[factor_name] = (df["tp"] - df["ma"]) / (df["md"] + eps)

    # # remove intermediate data
    del df["oma"]
    del df["hma"]
    del df["lma"]
    del df["cma"]
    del df["tp"]
    del df["ma"]
    del df["abs_diff_close"]
    del df["md"]

    return df

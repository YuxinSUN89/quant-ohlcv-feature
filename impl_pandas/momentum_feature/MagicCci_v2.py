def signal(df, n, factor_name, config):
    # MagicCci_v2 indicator (CCI using HLC average as typical price, EWM-based)
    # Formula: TP = (EMA(H,N) + EMA(L,N) + EMA(C,N)) / 3
    #          MA = EMA(TP, N); MD = EMA(|TP - MA|, N)
    #          result = (TP - MA) / MD
    # A variant of CCI using only HLC (no open) EWM-smoothed as the typical price.
    # Note: when using this indicator, n cannot be greater than half the number of filtered candles (not half the number of fetched candles)
    # df['oma'] = df['open'].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["hma"] = df["high"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["lma"] = df["low"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["cma"] = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["tp"] = (df["hma"] + df["lma"] + df["cma"]) / 3
    df["ma"] = df["tp"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["abs_diff_close"] = abs(df["tp"] - df["ma"])
    df["md"] = df["abs_diff_close"].ewm(span=n, adjust=config.ewm_adjust).mean()

    df[factor_name] = (df["tp"] - df["ma"]) / df["md"]

    # # delete intermediate data
    # del df['oma']
    del df["hma"]
    del df["lma"]
    del df["cma"]
    del df["tp"]
    del df["ma"]
    del df["abs_diff_close"]
    del df["md"]

    return df

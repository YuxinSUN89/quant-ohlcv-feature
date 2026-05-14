def signal(df, n, factor_name, config):
    # Ax10 indicator (TMA momentum × ATR volatility × taker buy composite)
    # Formula: TMA = MA(MA((HIGH+LOW)/2, N), N); MTM = CLOSE/(TMA+eps) - 1
    #          WD_ATR = ATR(N) / MA(CLOSE,N)  (normalized ATR)
    #          TAKER_BUY = MA(TAKER_BUY_QUOTE_VOLUME / MA(QUOTE_VOLUME,N) * 100, N)
    #          result = MA(MTM,N) * WD_ATR * TAKER_BUY * 1e8
    # Composite factor combining triangular MA momentum, ATR volatility, and taker buy pressure.
    # Scaled by 1e8 to amplify small values for practical use.
    eps = config.eps

    n1 = int(n)

    # ==============================================================
    ts = df[["high", "low"]].sum(axis=1) / 2

    close_ma = ts.rolling(n, min_periods=config.min_periods).mean()
    tma = close_ma.rolling(n, min_periods=config.min_periods).mean()
    df["mtm"] = df["close"] / (tma + eps) - 1

    df["mtm_mean"] = df["mtm"].rolling(window=n1, min_periods=config.min_periods).mean()

    # calculate volatility factor wd_atr based on price ATR
    df["c1"] = df["high"] - df["low"]
    df["c2"] = abs(df["high"] - df["close"].shift(1))
    df["c3"] = abs(df["low"] - df["close"].shift(1))
    df["tr"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["atr"] = df["tr"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["avg_price_"] = df["close"].rolling(window=n1, min_periods=config.min_periods).mean()
    df["wd_atr"] = df["atr"] / (df["avg_price_"] + config.eps)

    # average taker buy ratio
    df["vma"] = df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    df["taker_buy_ma"] = (df["taker_buy_quote_asset_volume"] / (df["vma"] + config.eps)) * 100
    df["taker_buy_mean"] = df["taker_buy_ma"].rolling(window=n, min_periods=config.min_periods).mean()

    indicator = "mtm_mean"

    # multiply mtm_mean indicator by three volatility factors
    df[indicator] = df[indicator] * df["wd_atr"] * df["taker_buy_mean"]
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
        "avg_price_",
        "vma",
        "taker_buy_ma",
        "taker_buy_mean",
    ]
    df = df.drop(columns=drop_col)

    return df

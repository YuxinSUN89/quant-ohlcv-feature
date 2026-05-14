def signal(df, n, factor_name, config):
    # Mtam indicator (Momentum × Taker buy ratio × ATR volatility composite)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; TAKER_RATIO = SUM(taker_buy,N)/SUM(quote_volume,N)
    #          WD_ATR = ATR(N) / MA(CLOSE,N); result = MA(MTM * TAKER_RATIO * WD_ATR, N)
    # Combines n-period price momentum with taker buy ratio (directional volume) and
    # normalized ATR (volatility). The rolling mean smooths out noise.
    # Positive values indicate momentum backed by buyer-initiated trades in a volatile market.

    # calculate momentum
    df["mtm"] = df["close"] / df["close"].shift(n) - 1

    # taker buy ratio
    volume = df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
    buy_volume = df["taker_buy_quote_asset_volume"].rolling(n, min_periods=config.min_periods).sum()
    df["taker_by_ratio"] = buy_volume / volume

    # volatility factor
    df["c1"] = df["high"] - df["low"]
    df["c2"] = abs(df["high"] - df["close"].shift(1))
    df["c3"] = abs(df["low"] - df["close"].shift(1))
    df["tr"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["atr"] = df["tr"].rolling(window=n, min_periods=config.min_periods).mean()
    df["avg_price_"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["wd_atr"] = df["atr"] / df["avg_price_"]

    # momentum * taker buy ratio * volatility
    df["mtm"] = df["mtm"] * df["taker_by_ratio"] * df["wd_atr"]
    df[factor_name] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean()

    drop_col = ["mtm", "taker_by_ratio", "c1", "c2", "c3", "tr", "atr", "wd_atr", "avg_price_"]
    df.drop(columns=drop_col, inplace=True)

    return df

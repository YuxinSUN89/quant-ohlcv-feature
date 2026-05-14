def signal(df, n, factor_name, config):
    # Cs_mtm_v2 indicator (Composite: price momentum × std momentum × volume momentum)
    # Formula: C_MTM = MA(CLOSE/REF(CLOSE,N)-1, N); S_MTM = MA(STD/REF(STD,N), N)
    #          V_MTM = MA(QUOTE_VOLUME/REF(QUOTE_VOLUME,N), N)
    #          result = C_MTM * S_MTM * V_MTM
    # Combines three rolling momentum signals: price, volatility, and volume.
    # High positive values indicate simultaneous upward trending in price, expanding volatility, and increasing volume.
    # close price momentum
    df["c_mtm"] = df["close"] / df["close"].shift(n) - 1
    df["c_mtm"] = df["c_mtm"].rolling(n, min_periods=config.min_periods).mean()
    # standard deviation momentum
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["s_mtm"] = df["std"] / df["std"].shift(n)
    df["s_mtm"] = df["s_mtm"].rolling(n, min_periods=config.min_periods).mean()
    # volume change
    df["v_mtm"] = df["quote_volume"] / df["quote_volume"].shift(n)
    df["v_mtm"] = df["v_mtm"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["c_mtm"] * df["s_mtm"] * df["v_mtm"]

    del df["c_mtm"], df["std"], df["s_mtm"], df["v_mtm"]

    return df

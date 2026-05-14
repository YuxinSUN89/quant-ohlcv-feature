def signal(df, n, factor_name, config):
    # CoppMinRoute indicator (COPP / normalized intraday shortest path)
    # Formula: ROUTE1 = (HIGH-OPEN) + (HIGH-LOW) + (CLOSE-LOW); ROUTE2 = (OPEN-LOW) + (HIGH-LOW) + (HIGH-CLOSE)
    #          MIN_ROUTE = MIN(ROUTE1, ROUTE2) / OPEN; EMA(MIN_ROUTE, N)
    #          RC = 100*(CLOSE/REF(CLOSE,N)-1 + CLOSE/REF(CLOSE,2N)-1); COPP = EMA(RC, N)
    #          result = COPP / EMA(MIN_ROUTE, N)
    # Divides the Coppock momentum signal by the smoothed intraday price path length (normalized by open).
    # Adjusts momentum for the efficiency of intraday price movement — shorter paths = cleaner momentum.
    eps = config.eps
    df["route_1"] = (df["high"] - df["open"]) + (df["high"] - df["low"]) + (df["close"] - df["low"])
    df["route_2"] = (df["open"] - df["low"]) + (df["high"] - df["low"]) + (df["high"] - df["close"])
    df["min_route"] = df[["route_1", "route_2"]].min(axis=1) / df["open"]  #  normalize shortest path

    df["RC"] = 100 * (df["close"] / df["close"].shift(n) - 1 + df["close"] / df["close"].shift(2 * n) - 1)
    df["RC"] = df["RC"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["min_route"] = df["min_route"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df[factor_name] = df["RC"] / (df["min_route"] + eps)

    return df

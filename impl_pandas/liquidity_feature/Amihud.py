def signal(df, n, factor_name, config):
    # Amihud indicator (Amihud illiquidity proxy via intraday shortest path)
    # Formula: ROUTE1 = 2*(HIGH-LOW) + (OPEN-CLOSE); ROUTE2 = 2*(HIGH-LOW) + (CLOSE-OPEN)
    #          SHORTEST_PATH = MIN(ROUTE1, ROUTE2); NORM_PATH = SHORTEST_PATH / OPEN
    #          LIQUIDITY_PREMIUM = QUOTE_VOLUME / NORM_PATH
    #          result = MA(LIQUIDITY_PREMIUM, N)
    # Adapts the Amihud illiquidity ratio using the intraday shortest price path as the price impact proxy.
    # Higher values indicate greater liquidity (more quote volume per unit of price movement).
    df["route_1"] = 2 * (df["high"] - df["low"]) + (df["open"] - df["close"])
    df["route_2"] = 2 * (df["high"] - df["low"]) + (df["close"] - df["open"])
    df.loc[df["route_1"] > df["route_2"], "intraday_shortest_path"] = df["route_2"]
    df.loc[df["route_1"] <= df["route_2"], "intraday_shortest_path"] = df["route_1"]
    df["normalized_shortest_path"] = df["intraday_shortest_path"] / df["open"]
    df["liquidity_premium"] = df["quote_volume"] / df["normalized_shortest_path"]

    df[factor_name] = df["liquidity_premium"].rolling(n, min_periods=2).mean()

    del df["route_1"]
    del df["route_2"]
    del df["intraday_shortest_path"]
    del df["normalized_shortest_path"]
    del df["liquidity_premium"]

    return df

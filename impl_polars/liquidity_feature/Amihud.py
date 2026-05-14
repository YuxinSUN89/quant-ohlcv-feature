import polars as pl


def signal(df, n, factor_name, config):
    # Amihud indicator (Amihud illiquidity proxy via intraday shortest path)
    # Formula: ROUTE1 = 2*(HIGH-LOW) + (OPEN-CLOSE); ROUTE2 = 2*(HIGH-LOW) + (CLOSE-OPEN)
    #          SHORTEST_PATH = MIN(ROUTE1, ROUTE2); NORM_PATH = SHORTEST_PATH / OPEN
    #          LIQUIDITY_PREMIUM = QUOTE_VOLUME / NORM_PATH
    #          result = MA(LIQUIDITY_PREMIUM, N)
    # Adapts the Amihud illiquidity ratio using the intraday shortest price path as the price impact proxy.
    # Higher values indicate greater liquidity (more quote volume per unit of price movement).
    df = df.with_columns(pl.Series("route_1", 2 * (df["high"] - df["low"]) + (df["open"] - df["close"])))
    df = df.with_columns(pl.Series("route_2", 2 * (df["high"] - df["low"]) + (df["close"] - df["open"])))
    df = df.with_columns(intraday_shortest_path=pl.min_horizontal([pl.col("route_1"), pl.col("route_2")]))
    df = df.with_columns(pl.Series("normalized_shortest_path", df["intraday_shortest_path"] / df["open"]))
    df = df.with_columns(pl.Series("liquidity_premium", df["quote_volume"] / df["normalized_shortest_path"]))

    df = df.with_columns(pl.Series(factor_name, df["liquidity_premium"].rolling_mean(n, min_samples=2)))

    df = df.drop(["route_1", "route_2", "intraday_shortest_path", "normalized_shortest_path", "liquidity_premium"])

    return df

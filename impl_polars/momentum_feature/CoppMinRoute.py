import polars as pl


def signal(df, n, factor_name, config):
    # CoppMinRoute indicator (COPP / normalized intraday shortest path)
    # Formula: ROUTE1 = (HIGH-OPEN) + (HIGH-LOW) + (CLOSE-LOW); ROUTE2 = (OPEN-LOW) + (HIGH-LOW) + (HIGH-CLOSE)
    #          MIN_ROUTE = MIN(ROUTE1, ROUTE2) / OPEN; EMA(MIN_ROUTE, N)
    #          RC = 100*(CLOSE/REF(CLOSE,N)-1 + CLOSE/REF(CLOSE,2N)-1); COPP = EMA(RC, N)
    #          result = COPP / EMA(MIN_ROUTE, N)
    # Divides the Coppock momentum signal by the smoothed intraday price path length (normalized by open).
    # Adjusts momentum for the efficiency of intraday price movement — shorter paths = cleaner momentum.
    eps = config.eps
    df = df.with_columns(
        pl.Series("route_1", (df["high"] - df["open"]) + (df["high"] - df["low"]) + (df["close"] - df["low"]))
    )
    df = df.with_columns(
        pl.Series("route_2", (df["open"] - df["low"]) + (df["high"] - df["low"]) + (df["high"] - df["close"]))
    )
    # normalize shortest path: MIN(ROUTE1, ROUTE2) / OPEN
    df = df.with_columns(min_route=pl.min_horizontal([pl.col("route_1"), pl.col("route_2")]) / df["open"])

    df = df.with_columns(
        pl.Series("RC", 100 * (df["close"] / (df["close"].shift(n) + config.eps) - 1 + df["close"] / (df["close"].shift(2 * n) + config.eps) - 1))
    )
    df = df.with_columns(pl.Series("RC", df["RC"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("min_route", df["min_route"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, df["RC"] / (df["min_route"] + eps)))

    return df

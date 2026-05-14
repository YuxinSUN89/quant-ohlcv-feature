import polars as pl


def signal(df, n, factor_name, config):
    # Mtam indicator (Momentum × Taker buy ratio × ATR volatility composite)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; TAKER_RATIO = SUM(taker_buy,N)/SUM(quote_volume,N)
    #          WD_ATR = ATR(N) / MA(CLOSE,N); result = MA(MTM * TAKER_RATIO * WD_ATR, N)
    # Combines n-period price momentum with taker buy ratio (directional volume) and
    # normalized ATR (volatility). The rolling mean smooths out noise.
    # Positive values indicate momentum backed by buyer-initiated trades in a volatile market.

    # calculate momentum
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))

    # taker buy ratio
    volume = df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
    buy_volume = df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("taker_by_ratio", buy_volume / volume))

    # volatility factor
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"].shift(1))))
    df = df.with_columns(tr=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("atr", df["tr"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("avg_price_", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("wd_atr", df["atr"] / (df["avg_price_"] + config.eps)))

    # momentum * taker buy ratio * volatility
    df = df.with_columns(pl.Series("mtm", df["mtm"] * df["taker_by_ratio"] * df["wd_atr"]))
    df = df.with_columns(pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    drop_col = ["mtm", "taker_by_ratio", "c1", "c2", "c3", "tr", "atr", "wd_atr", "avg_price_"]
    df = df.drop(drop_col)

    return df

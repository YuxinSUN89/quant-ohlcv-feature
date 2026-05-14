import polars as pl


def signal(df, n, factor_name, config):
    # MarketPl indicator
    eps = config.eps
    # MarketPl indicator (Market Placement / Average Holding Cost)
    # Formula: AVG_COST = EMA(QUOTE_VOLUME, N) / EMA(VOLUME, N); result = CLOSE / AVG_COST - 1
    # Computes EMA-weighted average holding cost (VWAP-like using EMA smoothing),
    # then measures how far the current close is above or below this cost.
    # Positive values suggest the current price is above average holding cost (profitable for holders).
    quote_volume_ema = df["quote_volume"].ewm_mean(span=n, adjust=config.ewm_adjust)
    volume_ema = df["volume"].ewm_mean(span=n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series("avg_holding_cost", quote_volume_ema / volume_ema))
    df = df.with_columns(pl.Series(factor_name, df["close"] / (df["avg_holding_cost"] + eps) - 1))

    df = df.drop("avg_holding_cost")

    return df

import polars as pl


def signal(df, n, factor_name, config):
    # AtrPct indicator (ATR N-period percentage change)
    # Formula: ATR = MA(TR, N); result = ATR.pct_change(N)
    # Measures the rate of change of ATR over N periods. Positive values indicate volatility is
    # expanding; negative values indicate volatility is contracting relative to N periods ago.
    df = df.with_columns(pl.Series("close_1", df["close"].shift()))
    tr = pl.max_horizontal([pl.col("high"), pl.col("low"), pl.col("close_1")]) - pl.min_horizontal(
        [pl.col("high"), pl.col("low"), pl.col("close_1")]
    )
    atr = df.select(tr.alias("tr"))["tr"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, atr.pct_change(n)))

    df = df.drop("close_1")

    return df

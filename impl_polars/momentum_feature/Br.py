import polars as pl


def signal(df, n, factor_name, config):
    # Br indicator (Bull-Bear Ratio)
    # Formula: BR = 100 * SUM(HIGH - REF(CLOSE,1), N) / SUM(REF(CLOSE,1) - LOW, N)
    # Similar to AR but uses the previous close as the reference instead of today's open.
    # Measures willingness to push price above yesterday's close vs. below it.
    # BR > 100 suggests bullish sentiment; BR < 100 suggests bearish sentiment.
    v1 = (df["high"] - df["close"].shift(1)).rolling_sum(n, min_samples=config.min_periods)
    v2 = (df["close"].shift(1) - df["low"]).rolling_sum(n, min_samples=config.min_periods)
    _br = 100 * v1 / v2
    df = df.with_columns(pl.Series(factor_name, _br))

    return df

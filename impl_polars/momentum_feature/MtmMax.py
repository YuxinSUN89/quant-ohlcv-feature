import polars as pl


def signal(df, n, factor_name, config):
    # MtmMax indicator (MTM vs rolling max of MTM)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; result = MTM - MAX(MTM, N).shift(1)
    # Measures how the current N-period momentum compares to the maximum momentum achieved over the past N periods.
    # Negative values indicate current momentum is below recent peak (momentum fading); 0 indicates new high.
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("up", df["mtm"].rolling_max(n, min_samples=config.min_periods).shift(1)))
    df = df.with_columns(pl.Series(factor_name, df["mtm"] - df["up"]))

    return df

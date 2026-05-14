import polars as pl


def signal(df, n, factor_name, config):
    # MtmMean indicator (Rolling mean of N-period momentum)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; result = MA(MTM, N)
    # Smooths the N-period momentum by taking its rolling mean, reducing noise.
    # Positive values indicate sustained upward price trend; negative indicates downward trend.
    df = df.with_columns(
        pl.Series(factor_name, (df["close"] / (df["close"].shift(n) + config.eps) - 1).rolling_mean(n, min_samples=config.min_periods))
    )

    return df

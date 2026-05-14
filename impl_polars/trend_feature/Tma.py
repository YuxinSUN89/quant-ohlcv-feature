import polars as pl


def signal(df, n, factor_name, config):
    # Tma indicator (Close vs double Moving Average)
    # Formula: MA1 = MA(CLOSE,N); MA2 = MA(MA1,N); result = CLOSE / (MA2 + eps) - 1
    # Uses a double-smoothed MA (Triangular MA) as the trend baseline.
    # Positive values indicate close is above the double MA (upward bias); negative below.
    eps = config.eps
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ma2", df["ma"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["close"] / (df["ma2"] + eps) - 1))

    # remove redundant columns
    df = df.drop(["ma", "ma2"])

    return df

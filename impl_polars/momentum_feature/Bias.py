import polars as pl


def signal(df, n, factor_name, config):
    # Bias indicator (Price deviation from MA)
    # Formula: BIAS = CLOSE / MA(CLOSE, N) - 1
    # Measures how far the close price deviates from its N-period moving average as a percentage.
    # Positive values indicate price is above MA (overbought potential); negative values indicate below MA (oversold potential).
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["close"] / (df["ma"] + config.eps) - 1)))

    df = df.drop("ma")

    return df

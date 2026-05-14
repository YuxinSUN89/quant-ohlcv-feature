import polars as pl


def signal(df, n, factor_name, config):
    # Bias_v13 indicator (Fast MA / Slow MA bias, rolling mean)
    # Formula: MAFAST = MA(CLOSE, N/2); MASLOW = MA(CLOSE, N)
    #          result = MA(MAFAST/MASLOW - 1, N)
    # Measures the smoothed ratio of a short-window MA to a long-window MA.
    # Positive values indicate short MA is consistently above long MA (uptrend); negative indicates downtrend.
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mafast", df["close"].rolling_mean(int(n / 2), min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series(factor_name, (df["mafast"] / (df["ma"] + config.eps) - 1).rolling_mean(n, min_samples=config.min_periods))
    )

    df = df.drop(["ma", "mafast"])

    return df

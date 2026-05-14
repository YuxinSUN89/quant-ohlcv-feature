import polars as pl


def signal(df, n, factor_name, config):
    # Bias_v14 indicator (Volume-weighted fast/slow MA bias, rolling mean)
    # Formula: MA = MA(CLOSE,N); MAFAST = MA(CLOSE,N/2)
    #          MTM = (MAFAST/MA - 1) * (QUOTE_VOLUME / MA(QUOTE_VOLUME,N))
    #          result = MA(MTM, N)
    # Volume-weighted version of the fast/slow MA bias (Bias_v13), amplified by relative quote volume.
    # Positive rolling mean indicates sustained volume-backed uptrend.
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ma2", df["close"].rolling_mean(int(n / 2), min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series(
            "mtm",
            (df["ma2"] / (df["ma"] + config.eps) - 1)
            * df["quote_volume"]
            / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop(["ma", "ma2", "mtm"])

    return df

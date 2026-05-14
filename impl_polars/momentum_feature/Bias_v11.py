import polars as pl


def signal(df, n, factor_name, config):
    # Bias_v11 indicator (Volume-weighted Bias with EMA smoothing)
    # Formula: BIAS = CLOSE/MA(CLOSE,N) - 1; VOL_RATIO = QUOTE_VOLUME / MA(QUOTE_VOLUME,N)
    #          MTM = BIAS * VOL_RATIO; result = EMA(MTM, N)
    # Volume-weighted price bias: amplifies signal when above-average volume accompanies the price deviation.
    # EMA smoothing reduces noise. High positive values indicate volume-backed upside momentum.
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series(
            "mtm",
            (df["close"] / (df["ma"] + config.eps) - 1)
            * df["quote_volume"]
            / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods),
        )
    )
    # EMA
    df = df.with_columns(pl.Series(factor_name, df["mtm"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.drop(["ma", "mtm"])

    return df

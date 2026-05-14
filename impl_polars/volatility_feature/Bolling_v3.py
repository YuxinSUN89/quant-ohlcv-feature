import polars as pl


def signal(df, n, factor_name, config):
    # Bolling_v3 indicator (Rate of change of the Bollinger upper band)
    # Formula: UPPER = MA(CLOSE,N) + 0.5*STD(CLOSE,N)
    #          result = (UPPER - REF(UPPER, 1)) / MA
    # Measures how fast the Bollinger upper band is moving relative to the MA.
    # Positive values indicate the upper band is expanding (rising volatility); negative values indicate contraction.
    eps = config.eps
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("upper", df["median"] + 0.5 * df["std"]))
    df = df.with_columns(pl.Series(factor_name, (df["upper"] - df["upper"].shift(1)) / (df["median"] + eps)))

    # delete extra columns
    df = df.drop(["median", "std", "upper"])

    return df

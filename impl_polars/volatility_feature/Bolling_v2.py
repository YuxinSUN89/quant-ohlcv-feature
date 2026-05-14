import polars as pl


def signal(df, n, factor_name, config):
    # Bolling_v2 indicator (Bollinger bandwidth with ±0.5σ bands)
    # Formula: UPPER = MA + 0.5*STD; LOWER = MA - 0.5*STD
    #          result = (UPPER - LOWER) / MA = STD / MA
    # Computes the normalized width of ±0.5σ Bollinger bands (= STD/MA, i.e., coefficient of variation).
    # Higher values indicate greater relative price dispersion; lower values indicate price compression.
    eps = config.eps
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("upper", df["median"] + 0.5 * df["std"]))
    df = df.with_columns(pl.Series("lower", df["median"] - 0.5 * df["std"]))
    df = df.with_columns(pl.Series(factor_name, (df["upper"] - df["lower"]) / (df["median"] + eps)))

    # delete extra columns
    df = df.drop(["median", "std", "upper", "lower"])

    return df

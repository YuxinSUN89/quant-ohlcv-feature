import polars as pl


def signal(df, n, factor_name, config):
    # Lcsd indicator (Low price vs Close MA ratio)
    # Formula: result = (LOW - MA(CLOSE, N)) / LOW
    # Measures how far the low price is below the rolling close MA, as a fraction of the low.
    # Negative values indicate the MA is above the low (price recently been higher than current low).
    eps = config.eps
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["low"] - df["median"]) / (df["low"] + eps)))

    # remove redundant columns
    df = df.drop("median")

    return df

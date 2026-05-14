import polars as pl


def signal(df, n, factor_name, config):
    """
    Build using hint as the B-selection factor
    """
    # ==============================================================

    df = df.with_columns(pl.Series("mtm", df["high"] / df["high"].shift(n) - 1))
    df = df.with_columns(pl.Series("mtm_mean", df["mtm"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("cm", df["close"] / (df["ma"] + config.eps)))
    df = df.with_columns(pl.Series(factor_name, (df["mtm_mean"] - df["cm"]) / df["cm"]))

    return df

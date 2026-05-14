import polars as pl


def signal(df, n, factor_name, config):
    """
    The maximum of average maximum drawdown and average maximum reverse drawdown over a period forms the Market Sentiment Stability Index.
    Market Sentiment Stability Index
    The smaller the indicator, the stronger the trend.
    """
    df = df.with_columns(pl.Series("max2here", df["high"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dd1here", abs(df["close"] / df["max2here"] - 1)))
    df = df.with_columns(pl.Series("avg_max_drawdown", df["dd1here"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series("min2here", df["low"].rolling_min(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dd2here", abs(df["close"] / df["min2here"] - 1)))
    df = df.with_columns(
        pl.Series("avg_reverse_drawdown", df["dd2here"].rolling_mean(n, min_samples=config.min_periods))
    )

    df = df.with_columns(factor_name_=pl.max_horizontal([pl.col("avg_max_drawdown"), pl.col("avg_reverse_drawdown")]))
    df = df.rename({"factor_name_": factor_name})

    df = df.drop("max2here")
    df = df.drop("dd1here")
    df = df.drop("avg_max_drawdown")
    df = df.drop("min2here")
    df = df.drop("dd2here")
    df = df.drop("avg_reverse_drawdown")

    return df

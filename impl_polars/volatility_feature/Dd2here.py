import polars as pl


def signal(df, n, factor_name, config):
    """
    Dd2here aims to construct a breakout-drawdown system, blacklisting for n hours when maximum drawdown exceeds a threshold
    """
    df = df.with_columns(pl.Series("max2here", df["high"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dd1here", abs(df["close"] / df["max2here"] - 1)))
    # df['avg_max_drawdown'] = df['dd1here'].rolling_mean(n, min_samples=config.min_periods)

    df = df.with_columns(pl.Series("min2here", df["low"].rolling_min(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dd2here", abs(df["close"] / df["min2here"] - 1)))
    # df['avg_reverse_drawdown'] = df['dd2here'].rolling_mean(n, min_samples=config.min_periods)

    df = df.with_columns(
        factor_name_=pl.min_horizontal([pl.col("dd1here"), pl.col("dd2here")]).rolling_max(
            n, min_samples=config.min_periods
        )
    )
    df = df.rename({"factor_name_": factor_name})
    drop_col = ["max2here", "dd1here", "min2here", "dd2here"]
    df = df.drop(drop_col)

    return df

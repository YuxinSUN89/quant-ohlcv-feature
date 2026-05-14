import polars as pl


def signal(df, n, factor_name, config):
    # Mtm multiplied by volatility, where volatility is expressed as the ratio of high to low
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(
        pl.Series(
            "volatility",
            df["high"].rolling_max(n, min_samples=config.min_periods)
            / df["low"].rolling_min(n, min_samples=config.min_periods)
            - 1,
        )
    )
    df = df.with_columns(
        pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods) * df["volatility"])
    )

    df = df.drop(["mtm", "volatility"])

    return df

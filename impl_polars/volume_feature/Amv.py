import polars as pl


def signal(df, n, factor_name, config):
    # AMV indicator
    """
    N1=13
    N2=34
    AMOV=VOLUME*(OPEN+CLOSE)/2
    AMV1=SUM(AMOV,N1)/SUM(VOLUME,N1)
    AMV2=SUM(AMOV,N2)/SUM(VOLUME,N2)
    AMV uses trading volume as a weight for the volume-weighted moving average of the
    average of open and close prices. Higher-volume prices have a greater impact on the
    moving average result, reducing the influence of low-volume price fluctuations.
    A buy/sell signal is generated when the short-term AMV line crosses above/below the long-term AMV line.
    """
    df = df.with_columns(pl.Series("AMOV", df["volume"] * (df["open"] + df["close"]) / 2))
    df = df.with_columns(
        pl.Series(
            "AMV1",
            df["AMOV"].rolling_sum(n, min_samples=config.min_periods)
            / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
        )
    )
    # df['AMV2'] = df['AMOV'].rolling(n * 3).sum() / df['volume'].rolling(n * 3).sum()
    # normalize
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["AMV1"] - df["AMV1"].rolling_min(n, min_samples=config.min_periods))
            / (
                df["AMV1"].rolling_max(n, min_samples=config.min_periods)
                - df["AMV1"].rolling_min(n, min_samples=config.min_periods)
            ),
        )
    )  # normalize

    df = df.drop("AMOV")
    df = df.drop("AMV1")

    return df

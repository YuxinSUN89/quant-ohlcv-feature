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
    df["AMOV"] = df["volume"] * (df["open"] + df["close"]) / 2
    df["AMV1"] = (
        df["AMOV"].rolling(n, min_periods=config.min_periods).sum()
        / df["volume"].rolling(n, min_periods=config.min_periods).sum()
    )
    # df['AMV2'] = df['AMOV'].rolling(n * 3, min_periods=config.min_periods).sum() / df['volume'].rolling(n * 3, min_periods=config.min_periods).sum()
    # normalize
    df[factor_name] = (df["AMV1"] - df["AMV1"].rolling(n, min_periods=config.min_periods).min()) / (
        df["AMV1"].rolling(n, min_periods=config.min_periods).max()
        - df["AMV1"].rolling(n, min_periods=config.min_periods).min()
    )  # normalize

    del df["AMOV"]
    del df["AMV1"]

    return df

import polars as pl


def signal(df, n, factor_name, config):
    # PjcDistance indicator (Close vs mean absolute deviation)
    # Formula: MA = MA(CLOSE,N); MAD = MA(|CLOSE - MA|, N)
    #          DISTANCE = MAX(CLOSE - MAD, 0); result = DISTANCE / MAD - 1
    # Measures how far above the mean absolute deviation the current close price sits.
    # Positive values indicate price is significantly above typical deviation; 0 when close ≤ MAD.
    # calculate moving average
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    # calculate the absolute difference between closing price and moving average for each candle
    df = df.with_columns(pl.Series("cha", abs(df["close"] - df["median"])))
    # calculate mean deviation
    df = df.with_columns(pl.Series("ping_jun_cha", df["cha"].rolling_mean(n, min_samples=config.min_periods)))

    # initialize distance column
    df = df.with_columns(pl.Series("distance", [0.0] * len(df)))

    # set offset to 0 when closing price is less than or equal to mean deviation
    condition_0 = df["close"] <= df["ping_jun_cha"]
    condition_1 = df["close"] > df["ping_jun_cha"]
    df = df.with_columns(
        pl.when(condition_0)
        .then(0)
        .when(condition_1)
        .then(df["close"] - df["ping_jun_cha"])
        .otherwise(0)
        .alias("distance")
    )

    # calculate the offset ratio of closing price relative to mean deviation
    df = df.with_columns(pl.Series(factor_name, (df["distance"] / df["ping_jun_cha"]) - 1))

    df = df.drop(["median", "cha", "ping_jun_cha", "distance"])

    return df

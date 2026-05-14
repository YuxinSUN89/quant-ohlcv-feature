def signal(df, n, factor_name, config):
    # PjcDistance indicator (Close vs mean absolute deviation)
    # Formula: MA = MA(CLOSE,N); MAD = MA(|CLOSE - MA|, N)
    #          DISTANCE = MAX(CLOSE - MAD, 0); result = DISTANCE / MAD - 1
    # Measures how far above the mean absolute deviation the current close price sits.
    # Positive values indicate price is significantly above typical deviation; 0 when close ≤ MAD.
    # calculate moving average
    df["median"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    # calculate the absolute difference between closing price and moving average for each candle
    df["cha"] = abs(df["close"] - df["median"])
    # calculate mean deviation
    df["ping_jun_cha"] = df["cha"].rolling(n, min_periods=config.min_periods).mean()

    # set offset to 0 when closing price is less than or equal to mean deviation
    condition_0 = df["close"] <= df["ping_jun_cha"]
    condition_1 = df["close"] > df["ping_jun_cha"]
    df.loc[condition_0, "distance"] = 0
    df.loc[condition_1, "distance"] = df["close"] - df["ping_jun_cha"]

    # calculate the offset ratio of closing price relative to mean deviation
    df[factor_name] = (df["distance"] / df["ping_jun_cha"]) - 1

    del df["median"], df["cha"], df["ping_jun_cha"], df["distance"]

    return df

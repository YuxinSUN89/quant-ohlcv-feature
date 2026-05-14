def signal(df, n, factor_name, config):
    # Bolling indicator (Bollinger Band breakout distance)
    # Formula: UPPER = MA(CLOSE,N) + 1*STD(CLOSE,N); LOWER = MA(CLOSE,N) - 1*STD(CLOSE,N)
    #          distance = CLOSE - UPPER if CLOSE > UPPER; CLOSE - LOWER if CLOSE < LOWER; else 0
    #          result = distance / STD
    # Measures how far the price has broken outside the Bollinger bands, normalized by std.
    # Positive values indicate breakout above upper band; negative values indicate breakdown below lower band.
    eps = config.eps
    # calculate Bollinger upper and lower bands
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["upper"] = df["ma"] + 1.0 * df["std"]
    df["lower"] = df["ma"] - 1.0 * df["std"]
    df["distance"] = 0.0
    condition_1 = df["close"] > df["upper"]
    condition_2 = df["close"] < df["lower"]
    df.loc[condition_1, "distance"] = df["close"] - df["upper"]
    df.loc[condition_2, "distance"] = df["close"] - df["lower"]
    df[factor_name] = df["distance"] / (df["std"] + eps)

    # delete extra columns
    del df["std"], df["ma"], df["upper"], df["lower"]

    return df

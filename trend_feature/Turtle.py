def signal(df, n, factor_name, config):
    # Turtle indicator (Turtle channel breakout distance)
    # Formula: UP = MAX(MAX(OPEN,CLOSE), N) shifted by 1; DN = MIN(MIN(OPEN,CLOSE), N) shifted by 1
    #          d = CLOSE - UP if above channel; CLOSE - DN if below channel; 0 if inside
    #          result = d / (UP - DN + eps)
    # Measures how far price has broken out of the N-period Turtle channel, normalized by channel width.
    # Positive values signal upward breakout; negative signal downward breakout; 0 means inside channel.
    eps = config.eps
    # calculate Turtle
    df["open_close_high"] = df[["open", "close"]].max(axis=1)
    df["open_close_low"] = df[["open", "close"]].min(axis=1)
    # calculate atr
    df["c1"] = df["high"] - df["low"]
    df["c2"] = abs(df["high"] - df["close"].shift(1))
    df["c3"] = abs(df["low"] - df["close"].shift(1))
    # calculate upper/lower bands
    df["up"] = df["open_close_high"].rolling(window=n, min_periods=config.min_periods).max().shift(1)
    df["dn"] = df["open_close_low"].rolling(window=n, min_periods=config.min_periods).min().shift(1)
    # calculate std
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    # calculate atr
    df["tr"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["atr"] = df["tr"].rolling(window=n, min_periods=config.min_periods).mean()
    # set the region between upper and lower bands to 0
    condition_0 = (df["close"] <= df["up"]) & (df["close"] >= df["dn"])
    condition_1 = df["close"] > df["up"]
    condition_2 = df["close"] < df["dn"]
    df.loc[condition_0, "d"] = 0
    df.loc[condition_1, "d"] = df["close"] - df["up"]
    df.loc[condition_2, "d"] = df["close"] - df["dn"]
    df[factor_name] = df["d"] / (df["up"] - df["dn"] + eps)

    del df["up"], df["dn"], df["std"], df["tr"], df["atr"], df["d"]
    del df["open_close_high"], df["open_close_low"]
    del df["c1"], df["c2"], df["c3"]

    return df

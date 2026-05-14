import polars as pl


def signal(df, n, factor_name, config):
    # Turtle indicator (Turtle channel breakout distance)
    # Formula: UP = MAX(MAX(OPEN,CLOSE), N) shifted by 1; DN = MIN(MIN(OPEN,CLOSE), N) shifted by 1
    #          d = CLOSE - UP if above channel; CLOSE - DN if below channel; 0 if inside
    #          result = d / (UP - DN + eps)
    # Measures how far price has broken out of the N-period Turtle channel, normalized by channel width.
    # Positive values signal upward breakout; negative signal downward breakout; 0 means inside channel.
    eps = config.eps
    # calculate Turtle
    df = df.with_columns(open_close_high=pl.max_horizontal([pl.col("open"), pl.col("close")]))
    df = df.with_columns(open_close_low=pl.min_horizontal([pl.col("open"), pl.col("close")]))
    # calculate atr
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"].shift(1))))
    # calculate upper/lower bands
    df = df.with_columns(pl.Series("up", df["open_close_high"].rolling_max(n, min_samples=config.min_periods).shift(1)))
    df = df.with_columns(pl.Series("dn", df["open_close_low"].rolling_min(n, min_samples=config.min_periods).shift(1)))
    # calculate std
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)))
    # calculate atr
    df = df.with_columns(tr=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("atr", df["tr"].rolling_mean(n, min_samples=config.min_periods)))
    # set the region between upper and lower bands to 0
    condition_0 = (df["close"] <= df["up"]) & (df["close"] >= df["dn"])
    condition_1 = df["close"] > df["up"]
    condition_2 = df["close"] < df["dn"]
    df = df.with_columns(
        pl.when(condition_0)
        .then(pl.lit(0.0))
        .when(condition_1)
        .then(df["close"] - df["up"])
        .when(condition_2)
        .then(df["close"] - df["dn"])
        .otherwise(pl.lit(0.0))
        .alias("d")
    )
    df = df.with_columns(pl.Series(factor_name, df["d"] / (df["up"] - df["dn"] + eps)))

    df = df.drop(["up", "dn", "std", "tr", "atr", "d"])
    df = df.drop(["open_close_high", "open_close_low"])
    df = df.drop(["c1", "c2", "c3"])

    return df

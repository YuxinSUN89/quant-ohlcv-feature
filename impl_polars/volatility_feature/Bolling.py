import polars as pl


def signal(df, n, factor_name, config):
    # Bolling indicator (Bollinger Band breakout distance)
    # Formula: UPPER = MA(CLOSE,N) + 1*STD(CLOSE,N); LOWER = MA(CLOSE,N) - 1*STD(CLOSE,N)
    #          distance = CLOSE - UPPER if CLOSE > UPPER; CLOSE - LOWER if CLOSE < LOWER; else 0
    #          result = distance / STD
    # Measures how far the price has broken outside the Bollinger bands, normalized by std.
    # Positive values indicate breakout above upper band; negative values indicate breakdown below lower band.
    eps = config.eps
    # calculate Bollinger upper and lower bands
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)))
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("upper", df["ma"] + 1.0 * df["std"]))
    df = df.with_columns(pl.Series("lower", df["ma"] - 1.0 * df["std"]))
    df = df.with_columns(pl.lit(0).alias("distance"))
    condition_1 = df["close"] > df["upper"]
    condition_2 = df["close"] < df["lower"]
    df = df.with_columns(
        pl.when(condition_1).then(df["close"] - df["upper"]).otherwise(pl.col("distance")).alias("distance")
    )
    df = df.with_columns(
        pl.when(condition_2).then(df["close"] - df["lower"]).otherwise(pl.col("distance")).alias("distance")
    )
    df = df.with_columns(pl.Series(factor_name, df["distance"] / (df["std"] + eps)))

    # delete extra columns
    df = df.drop(["std", "ma", "upper", "lower"])

    return df

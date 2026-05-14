import polars as pl


def signal(df, n, factor_name, config):
    """
    N=20
    TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    ATR=MA(TR,N)
    MIDDLE=MA(CLOSE,N)
    """
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", (df["high"] - df["close"].shift(1)).abs()))
    df = df.with_columns(pl.Series("c3", (df["low"] - df["close"].shift(1)).abs()))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("_ATR", df["TR"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("middle", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("upper", df["middle"] + 2 * df["_ATR"]))
    df = df.with_columns(pl.Series("lower", df["middle"] - 2 * df["_ATR"]))

    df = df.with_columns(pl.lit(0).alias("count"))
    df = df.with_columns(pl.when(df["close"] > df["upper"]).then(1).otherwise(pl.col("count")).alias("count"))
    df = df.with_columns(pl.when(df["close"] < df["lower"]).then(-1).otherwise(pl.col("count")).alias("count"))
    df = df.with_columns(pl.Series(factor_name, df["count"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.drop(["upper", "lower", "count", "c1", "c2", "c3", "TR", "_ATR", "middle"])

    return df

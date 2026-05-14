import polars as pl


def signal(df, n, factor_name, config):
    # TMF indicator
    """
    N=80
    HIGH_TRUE=MAX(HIGH,REF(CLOSE,1))
    LOW_TRUE=MIN(LOW,REF(CLOSE,1))
    TMF=EMA(VOL*(2*CLOSE-HIGH_TRUE-LOW_TRUE)/(HIGH_TRUE-LOW_TRUE),N)/EMA(VOL,N)
    TMF is similar to CMF, both weighting volume by price. However, CMF uses CLV as the weight,
    while TMF uses the true low and true high prices, and takes a moving average rather than a sum.
    A buy signal is generated when TMF crosses above 0;
    a sell signal is generated when TMF crosses below 0.
    """
    df = df.with_columns(pl.Series("ref", df["close"].shift(1)))
    df = df.with_columns(max_high=pl.max_horizontal([pl.col("high"), pl.col("ref")]))
    df = df.with_columns(min_low=pl.min_horizontal([pl.col("low"), pl.col("ref")]))

    T = df["volume"] * (2 * df["close"] - df["max_high"] - df["min_low"]) / (df["max_high"] - df["min_low"])
    df = df.with_columns(
        pl.Series(
            factor_name,
            T.ewm_mean(span=n, adjust=config.ewm_adjust) / df["volume"].ewm_mean(span=n, adjust=config.ewm_adjust),
        )
    )

    df = df.drop("ref")
    df = df.drop("max_high")
    df = df.drop("min_low")

    return df

import polars as pl


def signal(df, n, factor_name, config):
    # OSC indicator
    """
    N=40
    M=20
    OSC=CLOSE-MA(CLOSE,N)
    OSCMA=MA(OSC,M)
    OSC reflects the degree to which the closing price deviates from its moving average.
    Buy/sell signals are generated when OSC crosses above/below OSCMA.
    """
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(2 * n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("OSC", df["close"] - df["ma"]))
    df = df.with_columns(pl.Series(factor_name, df["OSC"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop("ma")
    df = df.drop("OSC")

    return df

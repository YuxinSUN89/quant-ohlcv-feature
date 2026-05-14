import polars as pl


def signal(df, n, factor_name, config):
    # HLMA indicator
    """
    N1=20
    N2=20
    HMA=MA(HIGH,N1)
    LMA=MA(LOW,N2)
    The HLMA indicator replaces the close price in the ordinary moving average with the high and low prices
    to get HMA and LMA respectively. A buy/sell signal is generated when the close price crosses above HMA / crosses below LMA.
    """
    hma = df["high"].rolling_mean(n, min_samples=config.min_periods)
    lma = df["low"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("HLMA", hma - lma))
    df = df.with_columns(pl.Series("HLMA_mean", df["HLMA"].rolling_mean(n, min_samples=config.min_periods)))

    # normalize (remove units)
    df = df.with_columns(pl.Series(factor_name, df["HLMA"] / df["HLMA_mean"] - 1))

    df = df.drop("HLMA")
    df = df.drop("HLMA_mean")

    return df

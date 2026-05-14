import polars as pl


def signal(df, n, factor_name, config):
    # Dc indicator
    """
    N=20
    UPPER=MAX(HIGH,N)
    LOWER=MIN(LOW,N)
    MIDDLE=(UPPER+LOWER)/2
    The Dc indicator uses the N-period highest price and N-period lowest price to construct upper and lower price channels,
    then takes their average as the middle channel. A buy/sell signal is generated when the close price crosses above/below the middle channel.
    """
    dc = (
        df["high"].rolling_max(n, min_samples=config.min_periods)
        + df["low"].rolling_min(n, min_samples=config.min_periods)
    ) / 2.0
    df = df.with_columns(pl.Series(factor_name, df["close"] - dc))

    return df

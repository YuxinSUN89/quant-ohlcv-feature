import polars as pl


def signal(df, n, factor_name, config):
    # Hma
    eps = config.eps
    """
    N=20
    HMA=MA(HIGH,N)
    The HMA indicator is a simple moving average where the close price is replaced by the high price.
    A buy/sell signal is generated when the high price crosses above/below HMA.
    """
    hma = df["high"].rolling_mean(n, min_samples=config.min_periods)
    # normalize (remove units)
    df = df.with_columns(pl.Series(factor_name, (df["high"] - hma) / (hma + eps)))

    return df

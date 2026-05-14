import polars as pl


def signal(df, n, factor_name, config):
    # HmaSignal indicator
    """
    N=20
    HmaSignal=MA(HIGH,N)
    The HmaSignal indicator is a simple moving average where the close price is replaced by the high price.
    A buy/sell signal is generated when the high price crosses above/below HmaSignal.
    """
    hma = df["high"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, df["high"] - hma))

    return df

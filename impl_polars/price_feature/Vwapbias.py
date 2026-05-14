import polars as pl


def signal(df, n, factor_name, config):
    # Vwapbias indicator
    """
    Replace the close price in bias with vwap.

    VWAP=quote_volume/volume (volume-weighted average price within the period)
    MA=moving average of VWAP
    factor = VWAP / MA - 1 (normalize)

    """
    eps = config.eps
    df = df.with_columns(pl.Series("vwap", df["quote_volume"] / df["volume"]))
    ma = df["vwap"].rolling_mean(n, min_samples=config.min_periods)  # compute moving average
    df = df.with_columns(pl.Series(factor_name, df["vwap"] / (ma + eps) - 1))

    df = df.drop("vwap")

    return df

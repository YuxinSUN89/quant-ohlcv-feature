import polars as pl


def signal(df, n, factor_name, config):
    # BbiBias
    eps = config.eps
    """
    BBI=(MA(CLOSE,3)+MA(CLOSE,6)+MA(CLOSE,12)+MA(CLOSE,24))/4
    BBI averages moving averages of different lengths, combining the smoothness and lag
    of different moving averages. A buy/sell signal is generated when the close crosses above/below BBI.
    """
    # calculate BBI indicator to compute bias
    ma1 = df["close"].rolling_mean(n, min_samples=config.min_periods)
    ma2 = df["close"].rolling_mean(2 * n, min_samples=config.min_periods)
    ma3 = df["close"].rolling_mean(4 * n, min_samples=config.min_periods)
    ma4 = df["close"].rolling_mean(8 * n, min_samples=config.min_periods)
    # BBI=(MA(CLOSE,3)+MA(CLOSE,6)+MA(CLOSE,12)+MA(CLOSE,24))/4
    bbi = (ma1 + ma2 + ma3 + ma4) / 4
    df = df.with_columns(pl.Series(factor_name, df["close"] / (bbi + eps) - 1))

    return df

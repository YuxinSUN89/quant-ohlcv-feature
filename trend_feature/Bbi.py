def signal(df, n, factor_name, config):
    # Bbi
    eps = config.eps
    """
    BBI=(MA(CLOSE,3)+MA(CLOSE,6)+MA(CLOSE,12)+MA(CLOSE,24))/4
    BBI averages moving averages of different lengths, combining the smoothness and lag
    of different moving averages. A buy/sell signal is generated when the close crosses above/below BBI.
    """
    # calculate BBI indicator
    ma1 = df["close"].rolling(n, min_periods=config.min_periods).mean()
    ma2 = df["close"].rolling(2 * n, min_periods=config.min_periods).mean()
    ma3 = df["close"].rolling(4 * n, min_periods=config.min_periods).mean()
    ma4 = df["close"].rolling(8 * n, min_periods=config.min_periods).mean()
    # BBI=(MA(CLOSE,3)+MA(CLOSE,6)+MA(CLOSE,12)+MA(CLOSE,24))/4
    bbi = (ma1 + ma2 + ma3 + ma4) / 4
    df[factor_name] = bbi / (df["close"] + eps)

    return df

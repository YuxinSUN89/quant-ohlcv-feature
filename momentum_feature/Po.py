def signal(df, n, factor_name, config):
    # PO indicator
    """
    EMA_SHORT=EMA(CLOSE,9)
    EMA_LONG=EMA(CLOSE,26)
    PO=(EMA_SHORT-EMA_LONG)/EMA_LONG*100
    PO measures the rate of change between the short-term and long-term moving averages.
    A buy signal is generated when PO crosses above 0;
    a sell signal is generated when PO crosses below 0.
    """
    ema_short = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    ema_long = df["close"].ewm(span=n * 3, adjust=config.ewm_adjust).mean()
    df[factor_name] = (ema_short - ema_long) / ema_long * 100

    return df

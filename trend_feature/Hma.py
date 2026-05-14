def signal(df, n, factor_name, config):
    # Hma
    eps = config.eps
    """
    N=20
    HMA=MA(HIGH,N)
    The HMA indicator is a simple moving average where the close price is replaced by the high price.
    A buy/sell signal is generated when the high price crosses above/below HMA.
    """
    hma = df["high"].rolling(n, min_periods=config.min_periods).mean()
    # normalize (remove units)
    df[factor_name] = (df["high"] - hma) / (hma + eps)

    return df

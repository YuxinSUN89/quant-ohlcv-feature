def signal(df, n, factor_name, config):
    # HmaSignal indicator
    """
    N=20
    HmaSignal=MA(HIGH,N)
    The HmaSignal indicator is a simple moving average where the close price is replaced by the high price.
    A buy/sell signal is generated when the high price crosses above/below HmaSignal.
    """
    hma = df["high"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["high"] - hma

    return df

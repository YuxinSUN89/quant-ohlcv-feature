def signal(df, n, factor_name, config):
    """
    N=20
    BullPower=HIGH-EMA(CLOSE,N)
    BearPower=LOW-EMA(CLOSE,N)
    ER is a momentum indicator used to measure the bull/bear power balance in the market. In a bull market, people
    buy more greedily near the high price; the higher the BullPower, the stronger the current bull force.
    In a bear market, people may sell out of fear near the low price.
    The lower the BearPower, the stronger the current bear force. When both are greater than 0, it reflects that
    bulls currently dominate; when both are less than 0, bears dominate.
    If BearPower crosses above 0, a buy signal is generated;
    if BullPower crosses below 0, a sell signal is generated.
    """
    eps = config.eps
    ema = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(CLOSE,N)
    df["high"] - ema  # noqa: F841 -- BullPower=HIGH-EMA(CLOSE,N)
    bear_power = df["low"] - ema  # BearPower=LOW-EMA(CLOSE,N)
    df[factor_name] = bear_power / (ema + eps)  # normalize

    return df

def signal(df, n, factor_name, config):
    # Macd_v2 indicator (MACD using (H+L)/2 price)
    # Formula: PRICE = (HIGH+LOW)/2; EMA1 = EMA(PRICE,N); EMA2 = EMA(PRICE,2N)
    #          DIF = EMA1 - EMA2; DEA = EMA(DIF, N/2); result = 10 * (2*DIF - DEA)
    # A variant of MACD that uses the midpoint price (H+L)/2 instead of close.
    # The MACD histogram (2*DIF - DEA) × 10 captures momentum direction and strength.

    # calculate Macd indicator
    ema1 = (0.5 * df["high"] + 0.5 * df["low"]).ewm(span=n, adjust=config.ewm_adjust).mean()
    ema2 = (0.5 * df["high"] + 0.5 * df["low"]).ewm(span=2 * n, adjust=config.ewm_adjust).mean()

    dif = ema1 - ema2
    dea = dif.ewm(span=int(n / 2.0), adjust=config.ewm_adjust).mean()

    df[factor_name] = 10 * (2 * dif - dea)

    return df

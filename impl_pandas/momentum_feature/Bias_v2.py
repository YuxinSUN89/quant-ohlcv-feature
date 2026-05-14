import talib as ta


def signal(df, n, factor_name, config):
    # Bias_v2 indicator (Volume-weighted bias on regression-smoothed close)
    # Formula: CLOSE_REG = EMA(LINEARREG(CLOSE,N), N); MA = MA(CLOSE_REG, N)
    #          CLOSE_HL = (HIGH + LOW)/2 * VOLUME; result = CLOSE_HL / MA - 1
    # Uses linear regression followed by EMA to smooth the close, then computes bias of
    # volume-weighted midpoint price relative to the smoothed MA.
    eps = config.eps
    # calculate linear regression
    df["new_close"] = ta.LINEARREG(df["close"], timeperiod=n)
    # smooth the curve again with EMA
    df["new_close"] = ta.EMA(df["new_close"], timeperiod=n)
    # calculate middle band using the new close price
    ma = df["new_close"].rolling(n, min_periods=config.min_periods).mean()
    # redefine close as (high + low) / 2 * volume
    # df['close'] =   (df['high'] + df['low']) / 2 * df['volume']
    close = (df["high"] + df["low"]) / 2 * df["volume"]
    # calculate bias
    df[factor_name] = close / (ma + eps) - 1

    del df["new_close"]

    return df

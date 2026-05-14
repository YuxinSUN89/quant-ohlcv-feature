import talib as ta


def signal(df, n, factor_name, config):
    # RegEma indicator (Close vs linear regression of EMA)
    # Formula: EMA = EMA(CLOSE, N); REG_EMA = LINEARREG(EMA, N); result = CLOSE / REG_EMA - 1
    # Measures deviation of close from the linear regression trend fitted to the EMA.
    # EMA smoothing reduces noise in the regression; the resulting signal shows how far close
    # strays from the smooth trend line.
    eps = config.eps
    ema = df["close"].ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    reg_close = ta.LINEARREG(ema, timeperiod=n)
    df[factor_name] = df["close"] / (reg_close + eps) - 1

    return df

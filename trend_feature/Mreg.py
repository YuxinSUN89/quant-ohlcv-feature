import talib as ta


def signal(df, n, factor_name, config):
    # Mreg indicator (Rolling mean of close vs linear regression residual)
    # Formula: REG = LINEARREG(CLOSE, N); MREG = CLOSE/REG - 1; result = MA(MREG, N)
    # Measures how much close deviates from its linear regression trend, then smooths with rolling mean.
    # Captures sustained over/under-performance relative to the trend line.
    df["reg_close"] = ta.LINEARREG(df["close"], timeperiod=n)  # talib built-in linear regression
    df["mreg"] = df["close"] / df["reg_close"] - 1
    df[factor_name] = df["mreg"].rolling(n, min_periods=config.min_periods).mean()

    # remove redundant columns
    del df["reg_close"], df["mreg"]

    return df

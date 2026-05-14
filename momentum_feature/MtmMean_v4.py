import talib as ta


def signal(df, n, factor_name, config):
    # MtmMean_v4 indicator (Linear regression of N-period momentum)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; result = LINEARREG(MTM, N)
    # Applies a linear regression fit to the momentum series, returning the regression value.
    # Smoother than rolling mean; captures the trend in momentum rather than its average.
    df["mtm"] = df["close"] / df["close"].shift(n) - 1
    df[factor_name] = ta.LINEARREG(df["mtm"], timeperiod=n)

    return df

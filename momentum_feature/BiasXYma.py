def signal(*args):
    # BiasXYma indicator (smoothed dual-MA spread)
    # Formula: BiasXYma = MA(MA_X - MA_Y, n); X=3, Y=6 by default
    # n-day moving average of the (3-day MA - 6-day MA) spread.
    # A smoothed short-vs-medium-term trend gauge; positive means short-term price is running above medium-term.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    X, Y = 3, 6

    bias_xy = df['close'].rolling(X, min_periods=1).mean() - df['close'].rolling(Y, min_periods=1).mean()
    df[factor_name] = bias_xy.rolling(n, min_periods=1).mean()

    return df

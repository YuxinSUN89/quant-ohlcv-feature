eps = 1e-8


def scale_01(s, n):
    # min-max normalize `s` against its own rolling n-period range
    roll_min = s.rolling(n, min_periods=1).min()
    roll_max = s.rolling(n, min_periods=1).max()
    return (s - roll_min) / (eps + roll_max - roll_min)


def signal(*args):
    # BiasXY indicator (normalized dual-MA bias)
    # Formula: BiasXY = (MA_X - MA_Y - MA((MA_X - MA_Y), n)) min-max normalized over n; X=3, Y=6 by default
    # Deviation of the (short MA - long MA) spread from its own n-day moving average, min-max normalized over n.
    # Near 1 means the spread is stretched to a local extreme relative to recent history; near 0 means it's compressed.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    X, Y = 3, 6

    bias_xy = df['close'].rolling(X, min_periods=1).mean() - df['close'].rolling(Y, min_periods=1).mean()
    bias_xy_ma = bias_xy.rolling(n, min_periods=1).mean()
    dev = bias_xy - bias_xy_ma
    df[factor_name] = scale_01(dev, n)

    return df

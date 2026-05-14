import numpy as np


def signal(df, n, factor_name, config):
    # ******************** KAMA ********************
    # N=10
    # N1=2
    # N2=30
    # DIRECTION=CLOSE-REF(CLOSE,N)
    # VOLATILITY=SUM(ABS(CLOSE-REF(CLOSE,1)),N)
    # ER=DIRETION/VOLATILITY
    # FAST=2/(N1+1)
    # SLOW=2/(N2+1)
    # SMOOTH=ER*(FAST-SLOW)+SLOW
    # COF=SMOOTH*SMOOTH
    # KAMA=COF*CLOSE+(1-COF)*REF(KAMA,1)
    # The KAMA indicator is similar to VIDYA in that it incorporates the ER (Efficiency Ratio) into the moving average weight.
    # Its usage is similar to other moving averages. When the current trend is strong, the ER value is large, and KAMA assigns greater weight to the current price,
    # making KAMA follow price movements closely, reducing its lag; when the current trend is weak (e.g., in an oscillating market), the ER value is small,
    # KAMA assigns less weight to the current price, increasing KAMA's lag, making it smoother and avoiding too many trading signals.
    # Unlike VIDYA, the KAMA indicator can set upper bound FAST and lower bound SLOW for the weight.
    eps = config.eps
    direction = df["close"] - df["close"].shift(1)
    volatility = df["close"].diff(1).abs().rolling(int(10 * n), min_periods=config.min_periods).sum()
    fast = 2 / (n / 5 + 1)
    slow = 2 / (3 * n + 1)

    _l = []
    # calculate kama
    for i, (c, d, v) in enumerate(zip(df["close"], direction, volatility)):
        if i < n:
            _l.append(0)
        else:
            er = np.divide(d, (v + eps))
            smooth = er * (fast - slow) + slow
            cof = smooth * smooth
            _l.append(cof * c + (1 - cof) * _l[-1])

    df[factor_name] = _l

    # df[factor_name] = ta.KAMA(df['close'], timeperiod=n)

    return df

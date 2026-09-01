eps = 1e-8


def signal(*args):
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # CMF indicator
    """
    N=60
    CMF=SUM(((CLOSE-LOW)-(HIGH-CLOSE))*VOLUME/(HIGH-LOW),N)/SUM(VOLUME,N)
    CMF weights volume using CLV. If the close price is above the midpoint of high and low,
    the volume is positive (buying power dominates); if the close price is below the midpoint,
    the volume is negative (selling power dominates).
    If CMF crosses above 0, a buy signal is generated;
    if CMF crosses below 0, a sell signal is generated.
    """
    A = ((df['close'] - df['low']) - (df['high'] - df['close']) )* df['volume'] / (df['high'] - df['low'] + eps)
    df[factor_name] = A.rolling(n).sum() / df['volume'].rolling(n).sum()

    return df

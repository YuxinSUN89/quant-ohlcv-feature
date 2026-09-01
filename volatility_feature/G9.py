eps = 1e-8


def signal(*args):
    # G9 indicator (midpoint-move range/volume oscillator, short window)
    # Formula: G9 = SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,7,2)
    # Same construction as G68 (midpoint change x range / volume) but smoothed over 7 periods instead of 15.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 7
    m = 2
    A = ((df['high'] + df['low']) / 2 - (df['high'].shift(1) + df['low'].shift(1)) / 2) * (df['high'] - df['low'] + eps) / (df['volume'] + eps)
    df['G9'] = A.ewm(alpha=m / n, adjust=False).mean()
    df[factor_name] = df['G9']
    df.drop(columns=['G9'], errors='ignore', inplace=True)

    return df

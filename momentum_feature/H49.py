import numpy as np


def signal(*args):
    # H49 indicator (acceleration/deceleration threshold switch)
    # Formula: H49 = (((((delay(CLOSE, 20) - delay(CLOSE, 10)) / 10) - ((delay(CLOSE, 10) - CLOSE) / 10)) < (-0.1)) ? 1 : (delay(CLOSE, 1) - CLOSE)))
    # Flags a strong deceleration in 10-day momentum (threshold -0.1); otherwise falls back to the 1-day price change (reversed sign).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    a = df['close'].shift(20)
    b = df['close'].shift(10)
    c = df['close'].shift()
    d = df['close']
    e = (a - b) / 10
    f = (b - d) / 10
    g = c - d
    df['H49'] = np.where((e - f < -0.1), 1, g)
    df[factor_name] = df['H49']
    df.drop(columns=['H49'], errors='ignore', inplace=True)

    return df

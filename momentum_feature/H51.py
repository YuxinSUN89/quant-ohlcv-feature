import numpy as np


def signal(*args):
    # H51 indicator (acceleration/deceleration threshold switch, sensitive)
    # Formula: H51 = (((((delay(CLOSE, 20) - delay(CLOSE, 10)) / 10) - ((delay(CLOSE, 10) - CLOSE) / 10)) < (-0.05)) ? 1 : (delay(CLOSE, 1) - CLOSE)))
    # Same construction as H49 but with a tighter deceleration threshold (-0.05), so it triggers more often.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 20
    m = 10
    a = (df['close'].shift(n) - df['close'].shift(m)) / m
    b = (df['close'].shift(m) - df['close']) / m
    c = df['close'].shift(1) - df['close']
    df['H51'] = np.where(((a - b) < -0.05), 1, c)
    df[factor_name] = df['H51']
    df.drop(columns=['H51'], errors='ignore', inplace=True)

    return df

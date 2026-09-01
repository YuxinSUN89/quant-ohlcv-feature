import numpy as np


def signal(*args):
    # G79 indicator (RSI-style up/down ratio, 12-period)
    # Formula: G79 = SMA(MAX(CLOSE-DELAY(CLOSE,1),0),12,1) / SMA(ABS(CLOSE-DELAY(CLOSE,1) ),12,1) * 100
    # Same up/down smoothing as G63/G67 at a 12-period window — a medium-speed RSI variant.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['temp1'] = np.maximum((df['close'] - df['close'].shift(1)), 0)
    df['temp2'] = abs(df['close'] - df['close'].shift(1))
    df['G79'] = df['temp1'].ewm(alpha=1 / 12, adjust=False).mean() / df['temp2'].ewm(alpha=1 / 12, adjust=False).mean() * 100
    df[factor_name] = df['G79']
    df.drop(columns=['temp1', 'temp2', 'G79'], errors='ignore', inplace=True)

    return df

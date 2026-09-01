import numpy as np


def signal(*args):
    # G21 indicator (regression slope of a 6-day moving average)
    # Formula: G21 = REGBETA(MEAN(CLOSE,6),SEQUENCE(6))
    # Linear-regression beta of the 6-day close moving average against a simple time index over 6 periods.
    # Positive values indicate the smoothed price trend is currently rising.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g21_0'] = df['close'].rolling(6, min_periods=1).mean()
    df['G21'] = df['g21_0'].rolling(6).apply(lambda x: np.polyfit([1, 2, 3, 4, 5, 6], x.tolist(), deg=1)[0])
    df[factor_name] = df['G21']
    df.drop(columns=['g21_0', 'G21'], errors='ignore', inplace=True)

    return df

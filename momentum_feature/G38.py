import numpy as np


def signal(*args):
    # G38 indicator (20-day high breakout momentum)
    # Formula: G38 = ((SUM(HIGH, 20) / 20) < HIGH) ? (-1 * DELTA(HIGH, 2)) : 0
    # When the 20-day average high is below today's high, returns the negative 2-day change in high; otherwise 0.
    # Nonzero only around fresh 20-day highs, flagging how fast the breakout is moving.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G38'] = np.where(df['high'].rolling(20).sum() / 20 < df['high'], -(df['high'] - df['high'].shift(2)), 0)
    df[factor_name] = df['G38']
    df.drop(columns=['G38'], errors='ignore', inplace=True)

    return df

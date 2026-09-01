import numpy as np


def signal(*args):
    # H9 indicator (sustained one-directional move detector)
    # Formula: H9 = (0 < ts_min(delta(CLOSE, 1), 5)) ? delta(CLOSE, 1) : ((ts_max(delta(CLOSE, 1), 5) < 0) ? delta(CLOSE, 1) : (-1 * delta(CLOSE, 1)))
    # Returns the 1-day price change unmodified if the last 5 days moved consistently in one direction, else returns it with the sign flipped.
    # Rewards sustained directional runs and penalizes moves that go against a recent consistent trend.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['h9_1'] = df['close'].diff(1)
    a = np.where(df['h9_1'].rolling(5).max() < 0, df['h9_1'], -1 * df['h9_1'])
    df['H9'] = np.where(0 < df['h9_1'].rolling(5).min(), df['h9_1'], a)
    df[factor_name] = df['H9']
    df.drop(columns=['h9_1', 'H9'], errors='ignore', inplace=True)

    return df

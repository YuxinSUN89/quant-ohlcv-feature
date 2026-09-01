import numpy as np
import pandas as pd


eps = 1e-8


def signal(*args):
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # FiRsi indicator
    # Formula: FI = VOLUME * (CLOSE - REF(CLOSE, 1)); RSI applied to FI series
    # Force Index (FI) combines price change and volume. RSI is then computed on FI to measure
    # whether buying or selling force is gaining momentum. EMA smoothing is applied at the end.
    # A value above 0.5 suggests increasing buying force; below 0.5 suggests selling force.
    df['_fi'] = df['volume'] * (df['close'] - df['close'].shift(1))

    diff = df['_fi'].diff()
    df['up'] = np.where(diff > 0, diff, 0)
    df['down'] = np.where(diff < 0, abs(diff), 0)
    A = df['up'].rolling(n,min_periods=1).sum()
    B = df['down'].rolling(n,min_periods=1).sum()
    RSI = A / (A + B + eps)

    s = RSI.ewm(span=n, adjust=False, min_periods=1).mean()
    df[factor_name] = pd.Series(s)

    del df['_fi']
    del df['up']
    del df['down']

    return df

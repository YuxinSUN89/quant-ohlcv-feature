import numpy as np


def signal(*args):
    # H53 indicator (change in close-location-value, alternate normalization)
    # Formula: H53 = (-1 * delta((((CLOSE - LOW) - (HIGH - CLOSE)) / (CLOSE - LOW)), 9))
    # 9-day change in ((close-low)-(high-close))/(close-low), negated (compare to G2's HIGH-LOW normalization).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    argument = np.where((df['close'] == df['low']), 0.00001, (df['close'] - df['low']))
    df['h53_0'] = np.where((df['high'] == df['close']), 0, (1 - (df['high'] - df['close']) / argument))
    df['H53'] = -df['h53_0'].diff(9)
    df[factor_name] = df['H53']
    df.drop(columns=['h53_0', 'H53'], errors='ignore', inplace=True)

    return df

import numpy as np


def signal(*args):
    # G173 indicator (smoothed +DI/-DI imbalance (duplicate formulation))
    # Formula: G173 = MEAN(ABS(SUM((LD>0 & LD>HD)?LD:0,14)*100/SUM(TR,14)-SUM((HD>0 & HD>LD)?HD:0,14)*100/SUM(TR,14))/(SUM((LD>0 & LD>HD)?LD:0,14)*100/SUM(TR,14)+SUM((HD>0 & HD>LD)?HD:0,14)*100/SUM(TR,14))*100,6)
    # Same construction as G172 — average absolute +DI/-DI imbalance from the ADX directional-movement system.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['a'] = df['close'].ewm(alpha=2 / 13, adjust=False).mean()
    df['b'] = df['a'].ewm(alpha=2 / 13, adjust=False).mean()
    df['c'] = np.log(df['close'])
    df['d'] = df['c'].ewm(alpha=2 / 13, adjust=False).mean()
    df['e'] = df['d'].ewm(alpha=2 / 13, adjust=False).mean()
    df['f'] = df['e'].ewm(alpha=2 / 13, adjust=False).mean()
    df['G173'] = df['a'] * 3 - df['b'] * 2 + df['f']
    df[factor_name] = df['G173']
    df.drop(columns=['a', 'b', 'c', 'd', 'e', 'f', 'G173'], errors='ignore', inplace=True)

    return df

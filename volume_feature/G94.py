import numpy as np


def signal(*args):
    # G94 indicator (30-day signed volume accumulator)
    # Formula: G94 = SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:(CLOSE<DELAY(CLOSE,1)?-VOLUME:0)),30)
    # Same construction as G84 (OBV-style running total) but over a 30-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g94_0'] = df['close'].shift(1)
    condition_1 = (df['close'] > df['g94_0'])
    condition_2 = (df['close'] < df['g94_0'])
    df['r_2'] = np.where(condition_2, -df['volume'], 0)
    df['r_1'] = np.where(condition_1, df['volume'], df['r_2'])
    df['G94'] = df['r_1'].rolling(30).sum()
    df[factor_name] = df['G94']
    df.drop(columns=['g94_0', 'r_2', 'r_1', 'G94'], errors='ignore', inplace=True)

    return df

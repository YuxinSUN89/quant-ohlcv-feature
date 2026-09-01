import numpy as np
import pandas as pd


def signal(*args):
    # G180 indicator (volume-conditioned reversal/rank factor)
    # Formula: G180 = (( MEAN(VOLUME,20) < VOLUME) ? (( -1 * TSRANK(ABS(DELTA(CLOSE, 7)), 60)) * SIGN(DELTA(CLOSE,7)) : (-1 * VOLUME)))
    # When volume exceeds its 20-day average, uses a signed rank of the 7-day price change; otherwise falls back to -volume.
    # A regime-switching factor — behaves as a reversal signal in high-volume periods and as a volume proxy otherwise.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g180_1'] = df['volume'].rolling(20, min_periods=1).mean()
    df['g180_2'] = df['close'] - df['close'].shift(7)
    df.loc[df['g180_2'] > 0, 'sign'] = 1
    df.loc[df['g180_2'] == 0, 'sign'] = 0
    df.loc[df['g180_2'] < 0, 'sign'] = -1
    df['tsrank'] = abs(df['g180_2']).rolling(60, min_periods=1).apply( lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['G180_a'] = -1 * df['tsrank'] * df['sign']
    df['G180_b'] = df['volume'] * -1
    condition = df['g180_1'] < df['volume']
    df['G180'] = np.where(condition, df['G180_a'], df['G180_b'])
    df[factor_name] = df['G180']
    df.drop(columns=['g180_1', 'g180_2', 'tsrank', 'G180_a', 'G180_b', 'G180', 'sign'], errors='ignore', inplace=True)

    return df

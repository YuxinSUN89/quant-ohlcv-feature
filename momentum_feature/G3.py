import numpy as np


def signal(*args):
    # G3 indicator (6-day sum of close deviation from the prior extreme)
    # Formula: G3 = SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),6)
    # On days where close changed, sums close minus the relevant prior extreme (prior close vs. low/high) over 6 days.
    # A momentum accumulator that only counts genuine directional moves, ignoring unchanged days.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 6
    df['g3_0'] = df['close'].shift()
    df['v0'] = df[['low', 'g3_0']].min(axis=1)
    df['v1'] = df[['high', 'g3_0']].max(axis=1)
    df['diff_close1'] = df['close'] - df['v0']
    df['diff_close2'] = df['close'] - df['v1']
    condition1 = df['close'] == df['g3_0']
    condition2 = df['close'] > df['g3_0']
    df['alpha'] = np.where(condition1, 0, np.where(condition2, df['diff_close1'], df['diff_close2']))
    df['G3'] = df['alpha'].rolling(n, min_periods=1).sum()
    df[factor_name] = df['G3']
    df.drop(columns=['g3_0', 'v0', 'v1', 'diff_close1', 'diff_close2', 'alpha', 'G3'], errors='ignore', inplace=True)

    return df

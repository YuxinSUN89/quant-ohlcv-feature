import numpy as np


def signal(*args):
    # G187 indicator (20-day sum of gap-up strength)
    # Formula: G187 = SUM((OPEN<=DELAY(OPEN,1)?0:MAX((HIGH-OPEN),(OPEN-DELAY(OPEN,1)))),20)
    # Sums the larger of (high-open) or (open-prior open) on days that gapped up, 0 otherwise, over 20 days.
    # Larger values indicate a recent history of strong gap-up opens.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G187_x'] = df['high'] - df['open']
    df['G187_y'] = df['open'] - df['open'].shift()
    df['G187_max'] = df[['G187_x', 'G187_y']].max(axis=1)
    df['G187_z'] = np.where(df['open'] <= df['open'].shift(), 0, df['G187_max'])
    df['G187'] = df['G187_z'].rolling(20).sum()
    df[factor_name] = df['G187']
    df.drop(columns=['G187_x', 'G187_y', 'G187_max', 'G187_z', 'G187'], errors='ignore', inplace=True)

    return df

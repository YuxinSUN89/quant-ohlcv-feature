import numpy as np


def signal(*args):
    # G129 indicator (sum of down-move magnitude)
    # Formula: G129 = SUM((CLOSE-DELAY(CLOSE,1)<0?ABS(CLOSE-DELAY(CLOSE,1)):0),12)
    # 12-day sum of the absolute size of down days only (0 on up days).
    # Larger values indicate heavier recent selling pressure.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G129_A'] = df['close'] - df['close'].shift(1)
    df['G129_?'] = np.where(df['G129_A'] < 0, abs(df['G129_A']), 0)
    df['G129'] = df['G129_?'].rolling(12).sum()
    df[factor_name] = df['G129']
    df.drop(columns=['G129_A', 'G129_?', 'G129'], errors='ignore', inplace=True)

    return df

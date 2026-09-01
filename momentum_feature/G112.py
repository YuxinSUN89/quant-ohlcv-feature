import numpy as np


def signal(*args):
    # G112 indicator (smoothed up/down move balance)
    # Formula: G112 = (SUM((CLOSE-DELAY(CLOSE,1)>0?CLOSE-DELAY(CLOSE,1):0),12)-SUM((CLOSE-DELAY(CLOSE,1)<0?ABS(CLOSE-DELAY(CLOSE,1)):0),12))/(SUM((CLOSE-DELAY(CLOSE,1)>0?CLOSE-DELAY(CLOSE,1):0),12)+SUM((CLOSE-DELAY(CLOSE,1)<0?ABS(CLOSE-DELAY(CLOSE,1)):0),12))*100
    # (Sum of up-moves minus sum of down-moves) / (sum of up-moves plus sum of down-moves) over 12 periods, scaled to +-100.
    # Close to +100 means moves have been almost entirely upward; close to -100 means almost entirely downward.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    diff = df['close'].diff()
    df['A1'] = np.where(diff > 0, diff, 0)
    df['A2'] = np.where(diff < 0, abs(diff), 0)
    A1 = df['A1'].rolling(12).sum()
    A2 = df['A2'].rolling(12).sum()
    df['G112'] = (A1 - A2) / (A1 + A2)
    df[factor_name] = df['G112']
    df.drop(columns=['A1', 'A2', 'G112'], errors='ignore', inplace=True)

    return df

import numpy as np


def signal(*args):
    # G137 indicator (intrabar directional-move ratio)
    # Formula: G137 = 16(CLOSE-DELAY(CLOSE,1)+(CLOSE OPEN)/2+DELAY(CLOSE,1)- DELAY(OPEN,1))/((ABS(HIGH -DELAY(CLOSE,1))>ABS(LOW- DELAY(CLOSE,1)) &ABS(HIGH DELAY(CLOSE,1))>ABS(HIGH -DELAY(LOW,1))?ABS(HIGH DELAY(CLOSE,1))+ABS(LOW -DELAY(CLOSE,1))/2+ABS(DELAY(CLOSE,1)- DELAY(OPEN,1))/4:(ABS(LOW -DELAY(CLOSE,1))>ABS(HIGH -DELAY(LOW,1)) &ABS(LOW- DELAY(CLOSE,1))>ABS(HIGH- DELAY(CLOSE,1))?ABS(LOW -DELAY(CLOSE,1))+ABS(HIGH- DELAY(CLOSE,1))/2+ABS(DELAY(CLOSE,1) -DELAY(OPEN,1))/4:ABS(HIGH -DELAY(LOW,1))+ABS(DELAY(CLOSE,1)- DELAY(OPEN,1))/4)))MAX(ABS(HIGH- DELAY(CLOSE,1)),ABS(LOW- DELAY(CLOSE,1)))
    # A DM-style ratio comparing today's directional price move to the larger of the up/down true ranges.
    # Larger positive values indicate the day's move was large relative to the prevailing true range.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['parta'] = df['close'] * 1.5 - df['open'] * 0.5 - df['open'].shift(1)
    df['condition1'] = np.logical_and( abs(df['high'] - df['close'].shift(1)) > abs(df['low'] - df['close'].shift(1)), abs(df['high'] - df['close'].shift(1)) > abs(df['high'] - df['low'].shift(1)))
    df['part2'] = abs(df['high'] - df['close'].shift(1)) + abs(df['low'] - df['close'].shift(1)) / 2 + abs( df['close'].shift(1) - df['open'].shift(1)) / 4
    df['condition2'] = np.logical_and( abs(df['low'] - df['close'].shift(1)) > abs(df['high'] - df['low'].shift(1)), abs(df['low'] - df['close'].shift(1)) > abs(df['high'] - df['close'].shift(1)))
    df['part4'] = abs(df['low'] - df['close'].shift(1)) + abs(df['high'] - df['close'].shift(1)) / 2 + abs( df['close'] - df['open']).shift(1) / 4
    df['part5'] = abs(df['high'] - df['low'].shift(1)) + abs(df['close'] - df['open']).shift(1) / 4
    df['part3'] = np.where(df['condition2'], df['part4'], df['part5'])
    df['partb'] = np.where(df['condition1'], df['part2'], df['part3'])
    df['part6'] = np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1)))
    df['G137'] = (df['parta'] / df['partb'] * df['part6'] * 16)
    df[factor_name] = df['G137']
    df.drop(columns=['parta', 'condition1', 'part2', 'condition2', 'part4', 'part5', 'part3', 'partb', 'part6', 'G137'], errors='ignore', inplace=True)

    return df

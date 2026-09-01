import numpy as np


def signal(*args):
    # G55 indicator (20-day accumulated intrabar directional-move ratio)
    # Formula: G55 = SUM(16*(CLOSE-DELAY(CLOSE,1)+(CLOSE-OPEN)/2+DELAY(CLOSE,1)-DELAY(OPEN,1))/((ABS(HIGH-DELAY(CL OSE,1))>ABS(LOW-DELAY(CLOSE,1)) & ABS(HIGH-DELAY(CLOSE,1))>ABS(HIGH-DELAY(LOW,1))?ABS(HIGH-DELAY(CLOSE,1))+ABS(LOW-DELAY(CLOS E,1))/2+ABS(DELAY(CLOSE,1)-DELAY(OPEN,1))/4:(ABS(LOW-DELAY(CLOSE,1))>ABS(HIGH-DELAY(LOW,1)) & ABS(LOW-DELAY(CLOSE,1))>ABS(HIGH-DELAY(CLOSE,1))?ABS(LOW-DELAY(CLOSE,1))+ABS(HIGH-DELAY(CLO SE,1))/2+ABS(DELAY(CLOSE,1)-DELAY(OPEN,1))/4:ABS(HIGH-DELAY(LOW,1))+ABS(DELAY(CLOSE,1)-DELAY(OP EN,1))/4)))*MAX(ABS(HIGH-DELAY(CLOSE,1)),ABS(LOW-DELAY(CLOSE,1))),20)
    # Sums, over 20 days, a scaled ratio of the day's net directional move to the larger of the up/down true ranges.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 20
    df['part1'] = 16 * ( df['close'] - df['close'].shift() + (df['close'] - df['open']) / 2 + df['close'].shift() - df[ 'open'].shift())
    condition1 = abs(df['high'] - df['close'].shift()) > abs(df['low'] - df['close'].shift())
    condition2 = abs(df['high'] - df['close'].shift()) > abs(df['high'] - df['low'].shift())
    df['value1'] = abs(df['high'] - df['close'].shift()) + \
                   abs(df['low'] - df['close'].shift()) / 2 + \
                   abs(df['close'].shift() - df['open'].shift()) / 4
    df['part2'] = np.where(condition1 & condition2, df['value1'], None)
    condition3 = abs(df['low'] - df['close'].shift()) > abs(df['high'] - df['low'].shift())
    condition4 = abs(df['low'] - df['close'].shift()) > abs(df['high'] - df['close'].shift())
    condition5 = df['part2'].isnull()
    df['value2'] = abs(df['low'] - df['close'].shift()) + \
                   abs(df['high'] - df['close'].shift()) / 2 + \
                   abs(df['close'].shift() - df['open'].shift()) / 4
    df.loc[condition3 & condition4 & condition5, 'part2'] = df['value2']
    df['value3'] = abs(df['high'] - df['low'].shift()) + \
                   abs(df['close'].shift() - df['open'].shift()) / 4
    df.loc[condition5, 'part2'] = df['value3']
    df['v4'] = abs(df['high'] - df['close'].shift())
    df['v5'] = abs(df['low'] - df['close'].shift())
    df['part3'] = df[['v4', 'v5']].max(axis=1)
    df['part2'] = df['part2'].replace(0, 1e-10)
    df['alpha'] = df['part1'] / df['part2'] * df['part3']
    df['G55'] = df['alpha'].rolling(n, min_periods=1).sum()
    df[factor_name] = df['G55']
    df.drop(columns=['part1', 'value1', 'part2', 'value2', 'value3', 'v4', 'v5', 'part3', 'alpha', 'G55'], errors='ignore', inplace=True)

    return df

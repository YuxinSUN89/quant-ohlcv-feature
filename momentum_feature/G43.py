import numpy as np


def signal(*args):
    # G43 indicator (6-day signed sum of traded value)
    # Formula: G43 = SUM((CLOSE>DELAY(CLOSE,1) ? AMOUNT : (CLOSE<DELAY(CLOSE,1)?-AMOUNT:0)),6)
    # Adds traded value (amount) on up days, subtracts it on down days, ignores flat days, over 6 periods.
    # A short-window money-flow accumulator; positive means buying value has dominated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H43_Q1A'] = df['close'] > df['close'].shift()
    df['H43_Q1B'] = df['quote_volume']
    df['H43_Q1C'] = np.where(df['close'] < df['close'].shift(), -df['quote_volume'], 0)
    df['H43_Q1'] = np.where(df['H43_Q1A'], df['H43_Q1B'], df['H43_Q1C'])
    df['G43'] = df['H43_Q1'].rolling(6).sum()
    df[factor_name] = df['G43']
    df.drop(columns=['H43_Q1A', 'H43_Q1B', 'H43_Q1C', 'H43_Q1', 'G43'], errors='ignore', inplace=True)

    return df

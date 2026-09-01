import numpy as np

eps = 1e-8


def signal(*args):
    # H41 indicator (geometric mean of high/low vs. VWAP)
    # Formula: H41 = (((HIGH * LOW)^0.5) - VWAP)
    # Compares the geometric mean of the day's high and low to the volume-weighted average price.
    # Positive values mean the bar's range midpoint sat above the volume-weighted price; negative means below.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['VWAP'] = df['quote_volume'] / (df['volume'] + eps)
    df['H41_prepare'] = (np.power((df['high'] * df['low']), 0.5) - df['VWAP']) / df['close'].shift()
    df['H41'] = df['H41_prepare']
    df[factor_name] = df['H41']
    df.drop(columns=['VWAP', 'H41_prepare', 'H41'], errors='ignore', inplace=True)

    return df

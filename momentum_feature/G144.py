import numpy as np

eps = 1e-8


def signal(*args):
    # G144 indicator (average down-day loss rate normalized by turnover)
    # Formula: G144 = SUMIF(ABS(CLOSE/DELAY(CLOSE,1)-1)/AMOUNT,20,CLOSE<DELAY(CLOSE,1))/COUNT(CLOSE<DELAY(CLOSE,1),20)
    # Average, over down days only in a 20-day window, of the absolute return divided by traded value.
    # Higher values mean down days have been producing outsized losses relative to how much value actually traded.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['prev_close'] = df['close'].shift(1)
    df['pct_chg'] = df['close'].pct_change()
    n = 20
    df['G144_part_12'] = np.where(df['close'] < df['prev_close'], abs(df['pct_chg']) / (df['quote_volume'] + eps), 0)
    df['G144_part_1'] = df['G144_part_12'].rolling(n, min_periods=1).sum()
    df['G144_part_22'] = np.where(df['close'] < df['prev_close'], 1, 0)
    df['G144_part_2'] = df['G144_part_22'].rolling(n, min_periods=1).sum()
    df['G144'] = df['G144_part_1'] / df['G144_part_2']
    df[factor_name] = df['G144']
    df.drop(columns=['G144_part_12', 'G144_part_1', 'G144_part_22', 'G144_part_2', 'G144', 'prev_close', 'pct_chg'], errors='ignore', inplace=True)

    return df

import numpy as np


def signal(*args):
    # G84 indicator (20-day signed volume accumulator)
    # Formula: G84 = SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:(CLOSE<DELAY(CLOSE,1)?-VOLUME:0)),20)
    # Adds volume on up days, subtracts it on down days, over 20 periods (an OBV-style running total, windowed).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    condition1 = df['close'] > df['close'].shift(1)
    condition2 = df['close'] < df['close'].shift(1)
    df['volume_x'] = np.where(condition1, df['volume'], np.where(condition2, df['volume'] * -1, 0))
    df['G84'] = df['volume_x'].rolling(20).sum()
    df[factor_name] = df['G84']
    df.drop(columns=['volume_x', 'G84'], errors='ignore', inplace=True)

    return df

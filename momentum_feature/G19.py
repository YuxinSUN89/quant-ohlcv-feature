import numpy as np


def signal(*args):
    # G19 indicator (asymmetric 5-day return)
    # Formula: G19 = (CLOSE<DELAY(CLOSE,5)?(CLOSE-DELAY(CLOSE,5))/DELAY(CLOSE,5):(CLOSE=DELAY(CLOSE,5)?0:(CLOSE-D ELAY(CLOSE,5))/CLOSE))
    # 5-day return measured against the prior close when price fell, or against the current close when it rose or was flat.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 5
    a = (df['close'] - df['close'].shift(n)) / df['close'].shift(n)
    b = (df['close'] - df['close'].shift(n)) / df['close']
    c = np.where(df['close'] == df['close'].shift(n), 0, b)
    df['G19'] = np.where(df['close'] < df['close'].shift(n), a, c)
    df[factor_name] = df['G19']
    df.drop(columns=['G19'], errors='ignore', inplace=True)

    return df

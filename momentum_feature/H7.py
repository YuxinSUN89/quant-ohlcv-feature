import numpy as np
import pandas as pd


def signal(*args):
    # H7 indicator (volume-conditioned reversal factor)
    # Formula: H7 = ((ADV20 < VOLUME) ? ((-1 * ts_rank(abs(delta(CLOSE, 7)), 60)) * sign(delta(CLOSE, 7))) : (-1 * 1))
    # When volume exceeds its 20-day average, uses a signed rank of the 7-day price change; otherwise returns -1 (compare to G180's -volume fallback).
    df = args[0]
    n = args[1]
    factor_name = args[2]

    df['adv20'] = df['volume'].rolling(20).mean()
    df['delta_close_7'] = df['close'].diff(7)
    df['h7_tsrank'] = df['delta_close_7'].abs().rolling(60, min_periods=1).apply(
        lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1]
    )
    df[factor_name] = np.where(
        df['volume'] > df['adv20'],
        -df['h7_tsrank'] * np.sign(df['delta_close_7']),
        -1,
    )
    df.drop(columns=['adv20', 'delta_close_7', 'h7_tsrank'], errors='ignore', inplace=True)

    return df

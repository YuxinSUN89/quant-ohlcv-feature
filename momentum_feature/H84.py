import numpy as np
import pandas as pd

eps = 1e-8


def signal(*args):
    # H84 indicator (signed-power VWAP-rank vs. price-delta exponent)
    # Formula: H84 = signedpower(ts_rank((VWAP - ts_max(VWAP, 15.3217)), 20.7127), delta(CLOSE, 4.96796))
    # Raises the rank of (VWAP relative to its 15-day high) to a power set by the recent price change, with sign preserved.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['VWAP'] = df['quote_volume'] / (df['volume'] + eps)
    df['h84_0'] = df['VWAP'] * df['close'] / df['close']
    df['ts_max_1'] = df['h84_0'].rolling(15).max()
    df['ts_rank'] = (df['h84_0']-df['ts_max_1']).rolling(21, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['delta_1'] = df['close'].diff(5)
    df['H84'] = np.sign(df['ts_rank']) * (abs(df['ts_rank'])**df['delta_1'])
    df[factor_name] = df['H84']
    df.drop(columns=['VWAP', 'h84_0', 'ts_max_1', 'ts_rank', 'delta_1', 'H84'], errors='ignore', inplace=True)

    return df

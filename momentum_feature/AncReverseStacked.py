import numpy as np


def signal(*args):
    # AncReverseStacked indicator (anchored-reversal factor on cumulative return (stacked variant))
    # Formula: n-day cumulative PCT_CHG = PREV_CLOSE.pct_change(n), high = MAX(CLOSE, m), low = MIN(CLOSE, m); m defaults to 30
    # Same anchoring logic as AncReverse, applied to build a stacked/aggregated reversal series.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['prev_close'] = df['close'].shift(1)
    n = int(n)
    m = int(30)
    df[f'ancreversestacked_1'] = df['prev_close'].pct_change(n)
    df[f'high_{m}'] = df['close'].rolling(window=m).max()
    df[f'low_{m}'] = df['close'].rolling(window=m).min()
    if n > m:
        raise ValueError(f"invalid arguments: n must be <= m (30); got n={n}, m={m}")
    elif n <= m:
        df[f'AncReverse_{n}_{m}'] = np.where(
            df[f'ancreversestacked_1'] < 0,
            df['close'] / df[f'high_{m}'] - 1,
            df['close'] / df[f'low_{m}'] - 1
        )
        df[f'ancreversestacked_0'] = df[f'AncReverse_{n}_{m}'] * (df['close'].pct_change().rolling(m).std())
    df[factor_name] = df[f'ancreversestacked_0']
    df.drop(columns=[f'ancreversestacked_1', f'high_{m}', f'low_{m}', f'AncReverse_{n}_{m}', f'ancreversestacked_0', 'prev_close'], errors='ignore', inplace=True)

    return df

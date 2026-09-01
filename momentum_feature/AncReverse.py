import numpy as np


def signal(*args):
    # AncReverse indicator (anchored-reversal factor on cumulative return)
    # Formula: n-day cumulative PCT_CHG = PREV_CLOSE.pct_change(n), high = MAX(CLOSE, m), low = MIN(CLOSE, m); m defaults to 30
    # Uses the n-day cumulative return instead of price level to anchor against the m-day high/low band.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['prev_close'] = df['close'].shift(1)
    n = int(n)
    m = int(30)
    df[f'ancreverse_0'] = df['prev_close'].pct_change(n)
    df[f'high_{m}'] = df['close'].rolling(window=m).max()
    df[f'low_{m}'] = df['close'].rolling(window=m).min()
    if n > m:
        raise ValueError(f"invalid arguments: n must be <= m (30); got n={n}, m={m}")
    elif n <= m:
        df[f'AncReverse_{n}_{m}'] = np.where(
            df[f'ancreverse_0'] < 0,
            df['close'] / df[f'high_{m}'] - 1,
            df['close'] / df[f'low_{m}'] - 1
        )
    df[factor_name] = df[f'AncReverse_{n}_{m}']
    df.drop(columns=[f'ancreverse_0', f'high_{m}', f'low_{m}', f'AncReverse_{n}_{m}', 'prev_close'], errors='ignore', inplace=True)

    return df

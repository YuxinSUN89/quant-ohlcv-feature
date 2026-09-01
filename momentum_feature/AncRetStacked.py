import numpy as np


def signal(*args):
    # AncRetStacked indicator (anchored-reversal factor (stacked variant))
    # Formula: short_ma = MA(CLOSE, n), high = MAX(CLOSE, m), low = MIN(CLOSE, m); m defaults to 30
    # Same anchoring logic as AncRet, applied to build a stacked/aggregated reversal series.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    m = int(30)
    df[f'ancretstacked_2'] = df['close'].rolling(n).mean()
    df[f'high_{m}'] = df['close'].rolling(window=m).max()
    df[f'low_{m}'] = df['close'].rolling(window=m).min()
    if n > m:
        raise ValueError(f"invalid arguments: n must be <= m (30); got n={n}, m={m}")
    elif n <= m:
        df[f'AncRet_{n}_{m}'] = np.where(
            df['close'] > df[f'ancretstacked_2'],
            df['close'] / df[f'low_{m}'] - 1,
            df['close'] / df[f'high_{m}'] - 1
        )
        df[f'ancretstacked_0'] = df[f'AncRet_{n}_{m}'] * (df['close'].pct_change().rolling(m).std())
    df[factor_name] = df[f'ancretstacked_0']
    df.drop(columns=[f'ancretstacked_2', f'high_{m}', f'low_{m}', f'AncRet_{n}_{m}', f'ancretstacked_0'], errors='ignore', inplace=True)

    return df

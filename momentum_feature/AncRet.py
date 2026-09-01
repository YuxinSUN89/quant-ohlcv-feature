import numpy as np


def signal(*args):
    # AncRet indicator (anchored-reversal factor)
    # Formula: short_ma = MA(CLOSE, n), high = MAX(CLOSE, m), low = MIN(CLOSE, m); m defaults to 30
    # Anchors to the short MA: above it, distance is measured to the m-day low; below it, to the m-day high.
    # A mean-reversion style factor — large magnitude flags price stretched away from its recent range.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    m = int(30)
    df[f'ancret_1'] = df['close'].rolling(n).mean()
    df[f'high_{m}'] = df['close'].rolling(window=m).max()
    df[f'low_{m}'] = df['close'].rolling(window=m).min()
    if n > m:
        raise ValueError(f"invalid arguments: n must be <= m (30); got n={n}, m={m}")
    elif n <= m:
        df[f'AncRet_{n}_{m}'] = np.where(
            df['close'] > df[f'ancret_1'],
            df['close'] / df[f'low_{m}'] - 1,
            df['close'] / df[f'high_{m}'] - 1
        )
    df[factor_name] = df[f'AncRet_{n}_{m}']
    df.drop(columns=[f'ancret_1', f'high_{m}', f'low_{m}', f'AncRet_{n}_{m}'], errors='ignore', inplace=True)

    return df

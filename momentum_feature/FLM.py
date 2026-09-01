import numpy as np


def signal(*args):
    # FLM indicator (recency of the period's best return)
    # Formula: FLM = position (periods back from today) of the max n-day PCT_CHG, divided by n
    # Locates how many periods ago (relative to n) the largest n-day return occurred.
    # Values near 1 mean the best move happened recently; values near 0 mean momentum has faded since its peak.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df[f'FLM_{n}'] = df['pct_chg'].rolling(n).apply(
        lambda x: (np.argmax(x) + 1) / len(x) if len(x) > 0 else np.NaN)
    df[factor_name] = df[f'FLM_{n}']
    df.drop(columns=[f'FLM_{n}', 'pct_chg'], errors='ignore', inplace=True)

    return df

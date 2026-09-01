def signal(*args):
    # MaxReturnN indicator (best n-day return from the recent low)
    # Formula: MaxReturnN = MAX(CLOSE / MIN(CLOSE, n) - 1, n)
    # Rolling max, over n days, of (close / n-day low - 1).
    # Captures the strongest rebound achieved from a recent trough within the window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'maxreturnn_1'] = df['close'].rolling(n, min_periods=1).min()
    df[f'ZF_{n}'] = df['close'] / df[f'maxreturnn_1'] - 1
    df[f'MDR_{n}'] = df[f'ZF_{n}'].rolling(n, min_periods=1).max()
    df[factor_name] = df[f'MDR_{n}']
    df.drop(columns=[f'maxreturnn_1', f'ZF_{n}', f'MDR_{n}'], errors='ignore', inplace=True)

    return df

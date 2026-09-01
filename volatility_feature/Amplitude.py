def signal(*args):
    # Amplitude indicator (n-day high/low amplitude)
    # Formula: Amplitude = MAX(HIGH, n) / MIN(LOW, n) - 1
    # n-day rolling high divided by n-day rolling low, minus 1.
    # Larger values indicate a wider trading range has opened up over the lookback window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    high = df['high'].rolling(n, min_periods=1).max()
    low = df['low'].rolling(n, min_periods=1).min()
    df[f'amplitude_0'] = high / (low + 1e-8) - 1
    df[factor_name] = df[f'amplitude_0']
    df.drop(columns=[f'amplitude_0'], errors='ignore', inplace=True)

    return df

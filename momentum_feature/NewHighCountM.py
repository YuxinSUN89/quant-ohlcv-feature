def signal(*args):
    # NewHighCountM indicator (count of N-day new highs within a trailing window)
    # Formula: NewHighCountM = total count of N-day new highs broken within the trailing M days
    # Counts how many times, within the trailing M days, price closed above its own trailing N-day high.
    # Higher counts indicate a persistent breakout regime rather than a single isolated new high.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    m = int(120)
    df[f'newhighcountm_1'] = df['high'].shift().rolling(min_periods=1, window=n).max()
    df[f'newhighcountm_3'] = (df['close'] > df[f'newhighcountm_1']).astype(int)
    df[f'newhighcountm_0'] = df[f'newhighcountm_3'].rolling(min_periods=1, window=m).sum()
    df[factor_name] = df[f'newhighcountm_0']
    df.drop(columns=[f'newhighcountm_1', f'newhighcountm_3', f'newhighcountm_0'], errors='ignore', inplace=True)

    return df

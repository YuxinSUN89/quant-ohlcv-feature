def signal(*args):
    # G57 indicator (smoothed stochastic %K (fast))
    # Formula: G57 = SMA((CLOSE - TSMIN(LOW,9))/ (TSMAX (HIGH,9) - TSMIN (LOW,9)) * 100,3,1)
    # A 3-period smoothed measure of where close sits within the 9-day high/low range, scaled to 0-100 — a fast stochastic %K.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G57_min'] = df['low'].rolling(9).min()
    df['G57_max'] = df['high'].rolling(9).max()
    df['G57_close_std'] = (df['close'] - df['G57_min']) / (df['G57_max'] - df['G57_min'])
    df['G57'] = (df['G57_close_std'] * 100).ewm(alpha=1.0 / 3, adjust=False).mean()
    df[factor_name] = df['G57']
    df.drop(columns=['G57_min', 'G57_max', 'G57_close_std', 'G57'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # G72 indicator (smoothed Williams %R-style oscillator, longer window)
    # Formula: G72 = SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,15,1)
    # Same construction as G47 but smoothed over 15 periods instead of 9.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 6
    m = 15
    e = 1
    df['period_high'] = df['high'].rolling(n, min_periods=0).max()
    df['period_low'] = df['low'].rolling(n, min_periods=0).min()
    df['var_A'] = (df['period_high'] - df['close']) / (df['period_high'] - df['period_low']) * 100
    df['G72'] = df['var_A'].ewm(alpha=e / m, adjust=False).mean()
    df[factor_name] = df['G72']
    df.drop(columns=['period_high', 'period_low', 'var_A', 'G72'], errors='ignore', inplace=True)

    return df

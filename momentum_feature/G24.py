def signal(*args):
    # G24 indicator (smoothed 5-day price change)
    # Formula: G24 = SMA(CLOSE-DELAY(CLOSE,5),5,1)
    # A smoothed version of the raw 5-day close-to-close difference.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 5
    m = 1
    df['A'] = df['close'] - df['close'].shift(5)
    df['G24'] = df['A'].ewm(alpha=m / n, adjust=False).mean()
    df[factor_name] = df['G24']
    df.drop(columns=['A', 'G24'], errors='ignore', inplace=True)

    return df

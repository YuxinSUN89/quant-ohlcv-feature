def signal(*args):
    # G22 indicator (smoothed change in normalized bias)
    # Formula: G22 = SMEAN(((CLOSE-MEAN(CLOSE, 6))/MEAN(CLOSE,6)-DELAY((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE, 6),3)), 12, 1)
    # A 12-period smoothed version of the 3-day change in (close - 6-day MA)/6-day MA.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['mean_6'] = df['close'].rolling(6).mean()
    df['A'] = (df['close'] - df['mean_6']) / df['mean_6']
    df['B'] = df['A'] - df['A'].shift(3)
    df['G22'] = df['B'].ewm(alpha=1 / 12, adjust=False).mean()
    df[factor_name] = df['G22']
    df.drop(columns=['mean_6', 'A', 'B', 'G22'], errors='ignore', inplace=True)

    return df

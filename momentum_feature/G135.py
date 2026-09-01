def signal(*args):
    # G135 indicator (smoothed lagged 20-day return ratio)
    # Formula: G135 = SMA(DELAY(CLOSE/DELAY(CLOSE,20),1),20,1)
    # A 20-period smoothed, one-day-lagged version of close / close-20-periods-ago.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G135'] = (df['close'] / df['close'].shift(20)).shift(1).ewm(alpha=1 / 20, adjust=False).mean()
    df[factor_name] = df['G135']
    df.drop(columns=['G135'], errors='ignore', inplace=True)

    return df

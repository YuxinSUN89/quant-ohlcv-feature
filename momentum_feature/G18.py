def signal(*args):
    # G18 indicator (5-day return ratio)
    # Formula: G18 = CLOSE/DELAY(CLOSE,5)
    # Close divided by the close 5 periods ago (unlike a plain pct_change, this is not offset by 1).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g18_0'] = df['close'].shift(5)
    df['G18'] = df['close'] / df['g18_0']
    df[factor_name] = df['G18']
    df.drop(columns=['g18_0', 'G18'], errors='ignore', inplace=True)

    return df

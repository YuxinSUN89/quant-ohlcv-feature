def signal(*args):
    # G14 indicator (5-day price change)
    # Formula: G14 = CLOSE - DELAY(CLOSE, 5)
    # Raw difference between today's close and the close 5 periods ago.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G14'] = df['close'] - df['close'].shift(5)
    df[factor_name] = df['G14']
    df.drop(columns=['G14'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # G106 indicator (20-day price change)
    # Formula: G106 = CLOSE-DELAY(CLOSE,20)
    # Raw difference between today's close and the close 20 periods ago.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G106'] = df['close'].diff(20)
    df[factor_name] = df['G106']
    df.drop(columns=['G106'], errors='ignore', inplace=True)

    return df

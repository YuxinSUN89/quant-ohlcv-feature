def signal(*args):
    # G15 indicator (overnight gap)
    # Formula: G15 = OPEN/DELAY(CLOSE,1)-1
    # Today's open relative to yesterday's close, expressed as a ratio minus 1.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G15'] = df['open'] / df['close'].shift(1) - 1
    df[factor_name] = df['G15']
    df.drop(columns=['G15'], errors='ignore', inplace=True)

    return df

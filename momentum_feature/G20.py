def signal(*args):
    # G20 indicator (6-day return, percent)
    # Formula: G20 = (CLOSE-DELAY(CLOSE,6))/DELAY(CLOSE,6)*100
    # 6-day percentage return, expressed on a 0-100 scale instead of a fraction.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G20'] = (df['close'] - df['close'].shift(6)) / df['close'].shift(6) * 100
    df[factor_name] = df['G20']
    df.drop(columns=['G20'], errors='ignore', inplace=True)

    return df

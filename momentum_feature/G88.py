def signal(*args):
    # G88 indicator (20-day return, percent)
    # Formula: G88 = (CLOSE-DELAY(CLOSE,20))/DELAY(CLOSE,20)*100
    # 20-day percentage return, expressed on a 0-100 scale instead of a fraction.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G88'] = (df['close'] - df['close'].shift(20)) / df['close'].shift(20) * 100
    df[factor_name] = df['G88']
    df.drop(columns=['G88'], errors='ignore', inplace=True)

    return df

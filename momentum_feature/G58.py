def signal(*args):
    # G58 indicator (20-day up-day frequency, percent)
    # Formula: G58 = COUNT(CLOSE>DELAY(CLOSE,1),20)/20*100
    # Fraction of the last 20 days that closed higher than the prior day, scaled to 0-100 (mirror of G53 at a longer window).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G58'] = (df['close'] > df['close'].shift(1)).rolling(20).sum() / 20 * 100
    df[factor_name] = df['G58']
    df.drop(columns=['G58'], errors='ignore', inplace=True)

    return df

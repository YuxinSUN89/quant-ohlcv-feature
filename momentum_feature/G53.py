def signal(*args):
    # G53 indicator (12-day up-day frequency, percent)
    # Formula: G53 = COUNT(CLOSE>DELAY(CLOSE,1),12)/12*100
    # Fraction of the last 12 days that closed higher than the prior day, scaled to 0-100.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n_G53 = 12
    count_true = df['close'] > df['close'].shift(1)
    df['count'] = 0.0
    df.loc[count_true, 'count'] = 1
    df['G53'] = df['count'].rolling(window=n_G53, min_periods=1).sum() / n_G53 * 100
    df[factor_name] = df['G53']
    df.drop(columns=['count', 'G53'], errors='ignore', inplace=True)

    return df

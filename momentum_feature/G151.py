def signal(*args):
    # G151 indicator (smoothed 20-day price change)
    # Formula: G151 = SMA(CLOSE-DELAY(CLOSE,20),20,1)
    # A smoothed version of the raw 20-day close-to-close difference.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g151_1'] = df['close'] - df['close'].shift(20) # CLOSE-DELAY(CLOSE,20)
    df['G151'] = df['g151_1'].ewm(alpha=1 / 20, adjust=False).mean()
    df[factor_name] = df['G151']
    df.drop(columns=['g151_1', 'G151'], errors='ignore', inplace=True)

    return df

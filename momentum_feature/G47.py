def signal(*args):
    # G47 indicator (smoothed Williams %R-style oscillator)
    # Formula: G47 = SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,9,1)
    # A smoothed measure of how far today's high sits below the 6-day high, relative to the 6-day range.
    # Higher values mean price is trading well off its recent high; lower values mean it is near the high.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['TSMAX_6'] = df['high'].rolling(6).max()
    df['TSMIN_6'] = df['low'].rolling(6).min()
    df['Var_A'] = (df['TSMAX_6'] - df['close']) * 100 / (df['TSMAX_6'] - df['TSMIN_6'])
    df['G47'] = df['Var_A'].ewm(alpha=1 / 9, adjust=False).mean()
    df[factor_name] = df['G47']
    df.drop(columns=['TSMAX_6', 'TSMIN_6', 'Var_A', 'G47'], errors='ignore', inplace=True)

    return df

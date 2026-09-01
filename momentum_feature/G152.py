def signal(*args):
    # G152 indicator (smoothed MACD-style oscillator on a lagged return ratio)
    # Formula: G152 = SMA(MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),12)-MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),26),9,1)
    # MACD-style fast/slow moving-average spread applied to a lagged, smoothed close-to-close ratio.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['p1'] = df['close'] / df['close'].shift(9) # CLOSE/DELAY(CLOSE,9)
    df['p2'] = df['p1'].shift(1) # DELAY(CLOSE/DELAY(CLOSE,9),1)
    df['p3'] = df['p2'].ewm(alpha=1.0 / 9, adjust=False).mean() # SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1)
    df['p4'] = df['p3'].shift(1) # DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1)
    df['p5'] = df['p4'].rolling(12,min_periods=1).mean() # PART1:MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),12)
    df['p6'] = df['p4'].rolling(26,min_periods=1).mean() # PART1:MEAN(DELAY(SMA(DELAY(CLOSE/DELAY(CLOSE,9),1),9,1),1),26)
    df['p7'] = df['p5'] - df['p6'] # PART1-PART2
    df['G152'] = df['p7'].ewm(alpha=1.0 / 9, adjust=False).mean() # SMA(PART1-PART2, 9, 1)
    df[factor_name] = df['G152']
    df.drop(columns=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'G152'], errors='ignore', inplace=True)

    return df

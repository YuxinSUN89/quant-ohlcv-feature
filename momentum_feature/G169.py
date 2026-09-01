def signal(*args):
    # G169 indicator (smoothed MACD-style oscillator on lagged price change)
    # Formula: G169 = SMA(MEAN(DELAY(SMA(CLOSE-DELAY(CLOSE,1),9,1),1),12)-MEAN(DELAY(SMA(CLOSE-DELAY(CLOSE,1),9,1),1), 26),10,1)
    # MACD-style fast/slow spread applied to a lagged, smoothed day-over-day price change.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['DSCDC'] = ((df['close'] - df['close'].shift(1)).ewm(alpha=1.0 / 9, adjust=False).mean()).shift(1)
    df['G169'] = (df['DSCDC'].rolling(12, min_periods=1).mean() - df['DSCDC'].rolling(26, min_periods=1).mean()).ewm(alpha=1.0 / 10, adjust=False).mean()
    df[factor_name] = df['G169']
    df.drop(columns=['DSCDC', 'G169'], errors='ignore', inplace=True)

    return df

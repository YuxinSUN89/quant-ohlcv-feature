def signal(*args):
    # G78 indicator (CCI-style typical-price deviation (Commodity Channel Index))
    # Formula: G78 = ((HIGH+LOW+CLOSE)/3-MA((HIGH+LOW+CLOSE)/3,12))/(0.015*MEAN(ABS(CLOSE-MEAN((HIGH+LOW+CLOSE)/3,12)),12))
    # Deviation of the typical price from its 12-day moving average, scaled by 0.015x its own mean absolute deviation — the standard CCI construction.
    # Values above +100 / below -100 are the conventional CCI overbought/oversold thresholds.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G78'] = ((df['high'] + df['low'] + df['close']) / 3 - ( (df['high'] + df['low'] + df['close']) / 3).rolling(12).mean()) / (0.015 * ( abs(df['close'] - ((df['high'] + df['low'] + df['close']) / 3).rolling(12).mean())).rolling(12).mean())
    df[factor_name] = df['G78']
    df.drop(columns=['G78'], errors='ignore', inplace=True)

    return df

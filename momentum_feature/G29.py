def signal(*args):
    # G29 indicator (6-day return weighted by volume)
    # Formula: G29 = (CLOSE-DELAY(CLOSE,6))/DELAY(CLOSE,6)*VOLUME
    # The 6-day percentage return multiplied by current volume.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G29'] = (df['close'] - df['close'].shift(6)) / (df['close'].shift(6) * df['volume'])
    df[factor_name] = df['G29']
    df.drop(columns=['G29'], errors='ignore', inplace=True)

    return df

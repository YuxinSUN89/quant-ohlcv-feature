def signal(*args):
    # G134 indicator (12-day return weighted by volume)
    # Formula: G134 = (CLOSE-DELAY(CLOSE,12))/DELAY(CLOSE,12)*VOLUME
    # The 12-day percentage return multiplied by current volume.
    # Emphasizes momentum readings that come with heavier trading activity.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G134'] = (df['close'] - df['close'].shift(12)) / df['close'].shift(12) * df['volume']
    df[factor_name] = df['G134']
    df.drop(columns=['G134'], errors='ignore', inplace=True)

    return df

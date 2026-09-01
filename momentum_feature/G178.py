def signal(*args):
    # G178 indicator (daily return weighted by volume)
    # Formula: G178 = (CLOSE-DELAY(CLOSE,1))/DELAY(CLOSE,1)*VOLUME
    # The 1-day percentage return multiplied by current volume.
    # Emphasizes short-term moves that come with heavier trading activity.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G178'] = (df['close'] - df['close'].shift()) / df['close'].shift() * df['volume']
    df[factor_name] = df['G178']
    df.drop(columns=['G178'], errors='ignore', inplace=True)

    return df

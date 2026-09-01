eps = 1e-8


def signal(*args):
    # G168 indicator (negative relative volume)
    # Formula: G168 = -1*VOLUME/MEAN(VOLUME,20)
    # Negative of current volume divided by its 20-day average.
    # Deeply negative values flag volume running well above its recent average.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G168'] = -1 * (df['volume'] / (df['volume'] + eps).rolling(20).mean())
    df[factor_name] = df['G168']
    df.drop(columns=['G168'], errors='ignore', inplace=True)

    return df

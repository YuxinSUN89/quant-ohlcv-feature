def signal(*args):
    # G139 indicator (negative open/volume correlation)
    # Formula: G139 = -1 * CORR(OPEN, VOLUME, 10)
    # Negative of the 10-day rolling correlation between the opening price and volume.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G139'] = -df['open'].rolling(10, min_periods=1).corr(df['volume'])
    df[factor_name] = df['G139']
    df.drop(columns=['G139'], errors='ignore', inplace=True)

    return df

eps = 1e-8


def signal(*args):
    # G80 indicator (5-day volume growth rate, percent)
    # Formula: G80 = (VOLUME-DELAY(VOLUME,5))/DELAY(VOLUME,5)*100
    # Percentage change in volume versus 5 periods ago.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G80'] = (df['volume'] - df['volume'].shift(5)) / (df['volume'] + eps).shift(5) * 100
    df[factor_name] = df['G80']
    df.drop(columns=['G80'], errors='ignore', inplace=True)

    return df

eps = 1e-8


def signal(*args):
    # G2 indicator (day-over-day change in close-location-value)
    # Formula: G2 = (-1 * DELTA((((CLOSE - LOW) - (HIGH - CLOSE)) / (HIGH - LOW)), 1))
    # 1-day change in ((close-low)-(high-close))/(high-low), negated.
    # Captures whether the close's position within its daily range is shifting toward the top or bottom of the bar.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G2_temp'] = (2 * df['close'] - df['low'] - df['high']) / (df['high'] - df['low'] + eps)
    df['G2'] = -1 * df['G2_temp'].diff(1)
    df[factor_name] = df['G2']
    df.drop(columns=['G2_temp', 'G2'], errors='ignore', inplace=True)

    return df

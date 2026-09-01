eps = 1e-8


def signal(*args):
    # G60 indicator (20-day sum of volume-weighted close-location-value)
    # Formula: G60 = SUM(((CLOSE-LOW)-(HIGH-CLOSE))./(HIGH-LOW).*VOLUME,20)
    # Same CLV-times-volume construction as G11, summed over a 20-day window instead of 6.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['temp'] = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + eps) * df[ 'quote_volume']
    df['G60'] = df['temp'].rolling(20).sum()
    df[factor_name] = df['G60']
    df.drop(columns=['temp', 'G60'], errors='ignore', inplace=True)

    return df

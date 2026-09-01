eps = 1e-8


def signal(*args):
    # G145 indicator (volume MACD-style oscillator)
    # Formula: G145 = (MEAN(VOLUME,9)-MEAN(VOLUME,26))/MEAN(VOLUME,12)*100
    # Difference between a fast (9-day) and slow (26-day) volume moving average, scaled by a 12-day volume average.
    # Positive values indicate short-term volume is running above its longer-term trend.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G145'] = (df['quote_volume'].rolling(9, min_periods=1).mean() - df['volume'].rolling(26, min_periods=1).mean()) / (df['volume'] + eps).rolling(12, min_periods=1).mean() * 100
    df[factor_name] = df['G145']
    df.drop(columns=['G145'], errors='ignore', inplace=True)

    return df

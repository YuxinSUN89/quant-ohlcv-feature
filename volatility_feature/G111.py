eps = 1e-8


def signal(*args):
    # G111 indicator (volume-weighted CLV, fast vs. slow smoothing)
    # Formula: G111 = SMA(VOL*((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW),11,2)-SMA(VOL*((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW),4,2)
    # Difference between an 11-period and a 4-period smoothed volume-weighted close-location-value series.
    # A positive/negative crossover-style read on whether buying pressure is accelerating or decelerating.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['A'] = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + eps)
    df['B'] = df['volume'] * df['A']
    df['SMA_1'] = df['B'].ewm(alpha=2 / 11, adjust=False).mean()
    df['SMA_2'] = df['B'].ewm(alpha=2 / 4, adjust=False).mean()
    df['G111'] = df['SMA_1'] - df['SMA_2']
    df[factor_name] = df['G111']
    df.drop(columns=['A', 'B', 'SMA_1', 'SMA_2', 'G111'], errors='ignore', inplace=True)

    return df

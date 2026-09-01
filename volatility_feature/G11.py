eps = 1e-8


def signal(*args):
    # G11 indicator (volume-weighted intrabar close position)
    # Formula: G11 = SUM(((CLOSE-LOW)-(HIGH-CLOSE))/(HIGH-LOW)*VOLUME,6)
    # Sums a CLV-style ((close-low)-(high-close))/(high-low) term weighted by volume over a 6-period window.
    # Positive and large when volume has concentrated on days closing near the high; negative when concentrated near the low.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 6
    df['G11'] = (((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + eps) * df[ 'volume']).rolling(n).sum()
    df[factor_name] = df['G11']
    df.drop(columns=['G11'], errors='ignore', inplace=True)

    return df

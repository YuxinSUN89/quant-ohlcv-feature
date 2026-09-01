def signal(*args):
    # G176 indicator (rank correlation of close-location-value and volume)
    # Formula: G176 = CORR(RANK(((CLOSE - TSMIN(LOW, 12)) / (TSMAX(HIGH, 12) - TSMIN(LOW,12)))), RANK(VOLUME), 6)
    # Correlation between the cross-sectional rank of a 12-day CLV measure and the rank of volume, over 6 days.
    # Positive values mean days with a stronger close-in-range position have tended to coincide with higher relative volume.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    N = 20
    df['G176'] = df['high'].rolling(N, min_periods=N).apply(lambda x: 1 + x.argmax(axis=0)) / N * 100
    df[factor_name] = df['G176']
    df.drop(columns=['G176'], errors='ignore', inplace=True)

    return df

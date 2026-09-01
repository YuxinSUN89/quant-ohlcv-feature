def signal(*args):
    # G133 indicator (recency of the 20-day high vs. 20-day low)
    # Formula: G133 = ((20-HIGHDAY(HIGH,20))/20)*100-((20-LOWDAY(LOW,20))/20)*100
    # Compares how many days ago the 20-day high occurred to how many days ago the 20-day low occurred.
    # Positive values mean the high is more recent than the low (uptrend bias); negative values mean the opposite.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    N = 20
    df['G133_HIGH_index'] = df['high'].shift().rolling(N, min_periods=20).apply(lambda x: x.argmax(axis=0))
    df['G133_LOW_index'] = df['low'].shift().rolling(N, min_periods=20).apply(lambda x: x.argmin(axis=0))
    df['G133'] = df['G133_HIGH_index'] / N * 100 - df['G133_LOW_index'] / N * 100
    df[factor_name] = df['G133']
    df.drop(columns=['G133_HIGH_index', 'G133_LOW_index', 'G133'], errors='ignore', inplace=True)

    return df

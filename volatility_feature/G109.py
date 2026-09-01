eps = 1e-8


def signal(*args):
    # G109 indicator (smoothed range relative to its own trend)
    # Formula: G109 = SMA(HIGH-LOW,10,2)/SMA(SMA(HIGH-LOW,10,2),10,2)
    # Ratio of a smoothed HIGH-LOW range to a further-smoothed version of itself.
    # Above 1 flags a range that is currently expanding relative to its own recent trend; below 1 flags contraction.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G109_SMA_1'] = (df['high'] - df['low'] + eps).ewm(alpha=(2 / 10), adjust=False).mean()
    df['G109_SMA_2'] = df['G109_SMA_1'].ewm(alpha=(2 / 10), adjust=False).mean()
    df['G109'] = df['G109_SMA_1'] / df['G109_SMA_2']
    df[factor_name] = df['G109']
    df.drop(columns=['G109_SMA_1', 'G109_SMA_2', 'G109'], errors='ignore', inplace=True)

    return df

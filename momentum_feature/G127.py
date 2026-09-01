def signal(*args):
    # G127 indicator (RMS deviation of close from its 12-day high)
    # Formula: G127 = (MEAN((100*(CLOSE-MAX(CLOSE,12))/(MAX(CLOSE,12)))2))1/2
    # Root-mean-square of the percentage gap between close and its rolling 12-day maximum.
    # Larger values mean price has been running persistently below its recent high.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g127_0'] = df['close'].rolling(12, min_periods=1).max()
    df['gtja127_1'] = (df['close'] / df['g127_0'] - 1) * 100
    df['gtja127_1'] = pow(df['gtja127_1'], 2)
    df['G127'] = df['gtja127_1'].rolling(12, min_periods=1).mean()
    df['G127'] = pow(df['G127'], 0.5)
    df[factor_name] = df['G127']
    df.drop(columns=['g127_0', 'gtja127_1', 'G127'], errors='ignore', inplace=True)

    return df

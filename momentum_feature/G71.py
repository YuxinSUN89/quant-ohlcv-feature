def signal(*args):
    # G71 indicator (24-day bias, percent)
    # Formula: G71 = (CLOSE-MEAN(CLOSE,24))/MEAN(CLOSE,24)*100
    # (close - 24-day MA) / 24-day MA on a 0-100 scale — the classic Bias indicator at a 24-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G71'] = (df['close'] - df['close'].rolling(window=24, min_periods=1).mean()) / df['close'].rolling(window=24, min_periods=1).mean() * 100
    df[factor_name] = df['G71']
    df.drop(columns=['G71'], errors='ignore', inplace=True)

    return df

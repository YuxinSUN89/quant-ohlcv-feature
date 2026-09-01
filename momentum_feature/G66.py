def signal(*args):
    # G66 indicator (6-day bias, percent)
    # Formula: G66 = (CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6)*100
    # (close - 6-day MA) / 6-day MA on a 0-100 scale — the classic Bias indicator at a 6-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G66'] = (df['close'] - df['close'].rolling(6).mean()) / df['close'].rolling(6).mean() * 100
    df[factor_name] = df['G66']
    df.drop(columns=['G66'], errors='ignore', inplace=True)

    return df

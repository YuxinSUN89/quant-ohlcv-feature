def signal(*args):
    # G31 indicator (12-day bias, percent)
    # Formula: G31 = (CLOSE-MEAN(CLOSE,12))/MEAN(CLOSE,12)*100
    # (close - 12-day MA) / 12-day MA, expressed on a 0-100 scale — the classic Bias indicator at a 12-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G31'] = (df['close'] - df['close'].rolling(12).mean()) / df['close'].rolling(12).mean() * 100
    df[factor_name] = df['G31']
    df.drop(columns=['G31'], errors='ignore', inplace=True)

    return df

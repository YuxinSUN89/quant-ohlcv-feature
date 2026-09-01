def signal(*args):
    # G65 indicator (6-day MA-to-close ratio)
    # Formula: G65 = MEAN(CLOSE,6)/CLOSE
    # 6-day moving average of close divided by current close (short-window inverse Bias, mirrors G34).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G65'] = df['close'].rolling(6).mean() / df['close']
    df[factor_name] = df['G65']
    df.drop(columns=['G65'], errors='ignore', inplace=True)

    return df

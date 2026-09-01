def signal(*args):
    # G34 indicator (12-day MA-to-close ratio)
    # Formula: G34 = MEAN(CLOSE,12)/CLOSE
    # 12-day moving average of close divided by the current close (inverse of a standard Bias ratio).
    # Above 1 means price sits below its recent average; below 1 means it sits above it.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G34'] = (df['close'].rolling(window=12, min_periods=12).mean() / df['close'])
    df[factor_name] = df['G34']
    df.drop(columns=['G34'], errors='ignore', inplace=True)

    return df

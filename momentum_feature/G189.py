def signal(*args):
    # G189 indicator (mean absolute deviation of close from its 6-day MA)
    # Formula: G189 = MEAN(ABS(CLOSE-MEAN(CLOSE,6)),6)
    # Average, over 6 days, of the absolute distance between close and its own 6-day moving average.
    # A dispersion measure of how far price typically strays from its short-term average.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    param = [6, 6]
    df['G189'] = df['close'].rolling(param[0], min_periods=1).mean()
    df['G189'] = (df['close'] - df['G189']).abs()
    df['G189'] = df['G189'].rolling(param[1], min_periods=1).mean()
    df[factor_name] = df['G189']
    df.drop(columns=['G189'], errors='ignore', inplace=True)

    return df

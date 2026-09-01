def signal(*args):
    # G153 indicator (average of four moving averages)
    # Formula: G153 = (MEAN(CLOSE,3)+MEAN(CLOSE,6)+MEAN(CLOSE,12)+MEAN(CLOSE,24))/4
    # Simple average of the 3-, 6-, 12- and 24-day moving averages of close.
    # A smoothed composite trend line blending several horizons.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['mean_3'] = df['close'].rolling(3, min_periods=1).mean()
    df['mean_6'] = df['close'].rolling(6, min_periods=1).mean()
    df['mean_12'] = df['close'].rolling(12, min_periods=1).mean()
    df['mean_24'] = df['close'].rolling(24, min_periods=1).mean()
    df['G153'] = (df['mean_3'] + df['mean_6'] + df['mean_12'] + df['mean_24']) / 4
    df[factor_name] = df['G153']
    df.drop(columns=['mean_3', 'mean_6', 'mean_12', 'mean_24', 'G153'], errors='ignore', inplace=True)

    return df

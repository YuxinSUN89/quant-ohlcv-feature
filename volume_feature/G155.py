def signal(*args):
    # G155 indicator (volume MACD-style oscillator (histogram form))
    # Formula: G155 = SMA(VOLUME,13,2)-SMA(VOLUME,27,2)-SMA(SMA(VOLUME,13,2)-SMA(VOLUME,27,2),10,2)
    # Volume MACD line (13 vs 27-period smoothed volume) minus its own 10-period signal line.
    # Positive values indicate volume momentum is accelerating relative to its own trend.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    temp = df['volume'].ewm(alpha=2 / 13, adjust=False).mean() - df['volume'].ewm(alpha=2 / 27, adjust=False).mean()
    df['G155'] = temp - temp.ewm(alpha=2 / 10, adjust=False).mean()
    df[factor_name] = df['G155']
    df.drop(columns=['G155'], errors='ignore', inplace=True)

    return df

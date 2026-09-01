def signal(*args):
    # G161 indicator (average true range (ATR-style))
    # Formula: G161 = MEAN(MAX(MAX((HIGH-LOW),ABS(DELAY(CLOSE,1)-HIGH)),ABS(DELAY(CLOSE,1)-LOW)),12)
    # Average, over 12 days, of the largest of: high-low, |prior close - high|, |prior close - low|.
    # A standard true-range volatility measure — higher values mean wider, more volatile bars.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df["G161_1"] = df['high'] - df['low']
    df["G161_2"] = (df['close'].shift(1) - df['high']).abs()
    df["G161_3"] = (df['close'].shift(1) - df['low']).abs()
    df["G161"] = df[["G161_1", "G161_2", "G161_3"]].max(axis=1).rolling(12).mean()
    df[factor_name] = df['G161']
    df.drop(columns=["G161_1", "G161_2", "G161_3", "G161"], errors='ignore', inplace=True)

    return df

def signal(*args):
    # G175 indicator (average true range, short window)
    # Formula: G175 = MEAN(MAX(MAX((HIGH-LOW),ABS(DELAY(CLOSE,1)-HIGH)),ABS(DELAY(CLOSE,1)-LOW)),6)
    # Same construction as G161 (true range averaged over the largest of three range measures) but over a 6-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 6
    df['A'] = df['high'] - df['low']
    df['B'] = (df['close'].shift(1) - df['high']).abs()
    df['C'] = (df['close'].shift(1) - df['low']).abs()
    df['D'] = df[['A', 'B', 'C']].max(axis=1, skipna=True)
    df['G175'] = df['D'].rolling(n, min_periods=1).mean()
    df[factor_name] = df['G175']
    df.drop(columns=['A', 'B', 'C', 'D', 'G175'], errors='ignore', inplace=True)

    return df

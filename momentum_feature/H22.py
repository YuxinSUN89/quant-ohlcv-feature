def signal(*args):
    # H22 indicator (smoothed change in normalized bias (duplicate formulation))
    # Formula: H22 = SMEAN(((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6)-DELAY((CLOSE-MEAN(CLOSE,6))/MEAN(CLOSE,6),3)),12,1)
    # Same construction as G22 — a smoothed 12-period series of the 3-day change in normalized 6-day bias.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H22_a'] =  (df['close'] - df['close'].rolling(6).mean())/(df['close'].rolling(6).mean())
    df['H22_b'] = df['H22_a'].shift(3)
    df['H22'] = (df['H22_a'] - df['H22_b']).ewm(alpha=1.0/12).mean()
    df[factor_name] = df['H22']
    df.drop(columns=['H22_a', 'H22_b', 'H22'], errors='ignore', inplace=True)

    return df

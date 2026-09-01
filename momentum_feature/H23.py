def signal(*args):
    # H23 indicator (20-day high breakout momentum (duplicate formulation))
    # Formula: H23 = (((sum(HIGH, 20) / 20) < HIGH) ? (-1 * delta(HIGH, 2)) : 0)
    # Same construction as G38 — nonzero only when today's high exceeds its 20-day average, flagging breakout speed.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['HIGH_20'] = df['high'].rolling(20,min_periods=1).mean()
    df.loc[df['HIGH_20'] < df['high'], 'H23'] = -1 * (df['high'] - df['high'].shift(2))
    df['H23'] = df['H23'].fillna(0)
    df[factor_name] = df['H23']
    df.drop(columns=['HIGH_20', 'H23'], errors='ignore', inplace=True)

    return df

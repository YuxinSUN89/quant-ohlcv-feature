def signal(*args):
    # H24 indicator (flat-trend mean reversion vs. momentum switch (duplicate formulation))
    # Formula: H24 = ((((delta((sum(CLOSE, 100) / 100), 100) / delay(CLOSE, 100)) < 0.05) || ((delta((sum(CLOSE, 100) / 100), 100) / delay(CLOSE, 100))== 0.05)) ? (-1 * (CLOSE - ts_min(CLOSE, 100))) : (-1 * delta(CLOSE, 3)))
    # Same construction as G98 — switches between distance-from-low and short-term momentum depending on how flat the 100-day trend has been.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H24_1'] = df['close'].rolling(100,min_periods=1).mean()
    df['H24_2'] = df['H24_1'].shift(100)
    df['H24_3'] = df['close'].shift(100)
    df['H24_4'] = (df['H24_1']-df['H24_2'])/df['H24_3']
    df['H24_5'] = -1 * (df['close'] - df['close'].shift(3))
    df['H24_6'] = -1 * (df['close'] - df['close'].rolling(100,min_periods=1).min())
    df.loc[df['H24_4'] <= 0.05, 'H24'] = df['H24_5']
    df.loc[df['H24_4'] > 0.05, 'H24'] = df['H24_6']
    df[factor_name] = df['H24']
    df.drop(columns=['H24_1', 'H24_2', 'H24_3', 'H24_4', 'H24_5', 'H24_6', 'H24'], errors='ignore', inplace=True)

    return df

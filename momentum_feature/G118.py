def signal(*args):
    # G118 indicator (upper vs. lower wick pressure)
    # Formula: G118 = SUM(HIGH - OPEN, 20) / SUM(OPEN - LOW, 20) * 100
    # Ratio of the 20-day sum of (high-open) to the 20-day sum of (open-low), scaled to 100.
    # Above 100 means upside wicks have dominated recently; below 100 means downside wicks have dominated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G118'] = (df['high'] - df['open']).rolling(20).sum() / (df['open'] - df['low']).rolling(20).sum() * 100
    df[factor_name] = df['G118']
    df.drop(columns=['G118'], errors='ignore', inplace=True)

    return df

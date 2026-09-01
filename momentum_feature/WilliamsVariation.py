def signal(*args):
    # WilliamsVariation indicator (dispersion of the intrabar body/range ratio, volume-weighted)
    # Formula: WilliamsVariation = STD((CLOSE - OPEN) / (HIGH - LOW) * QUOTE_VOLUME, n)
    # Rolling std of ((close-open)/(high-low)) x quote volume.
    # Higher values mean the balance of buying vs. selling pressure within each bar has been swinging erratically, at scale.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['A'] = df['close'] - df['open']
    df['B'] = df['high'] - df['low']
    df['williamsvariation_0'] = df['A'] / df['B'] * df['quote_volume']
    df[f'williamsvariation_1'] = df['williamsvariation_0'].rolling(n, min_periods=2).std()
    df[factor_name] = df[f'williamsvariation_1']
    df.drop(columns=['A', 'B', 'williamsvariation_0', f'williamsvariation_1'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # CsMtmV3 indicator (average return scaled by change in volatility)
    # Formula: CsMtmV3 = n-day average CLOSE return * n-day CLOSE std change
    # Multiplies the n-day average return by the change in the n-day return std.
    # Highlights moves where directional momentum is building alongside rising volatility.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['c_mtm'] = df['close'] / df['close'].shift(n) - 1
    df['c_mtm'] = df['c_mtm'].rolling(n, min_periods=1).mean()
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)
    df['s_mtm'] = df['std'] / df['std'].shift(n) - 1
    df['s_mtm'] = df['s_mtm'].rolling(n, min_periods=1).mean()
    df[f'CsMtmV3_{n}'] = df['c_mtm'] * df['s_mtm']
    df[factor_name] = df[f'CsMtmV3_{n}']
    df.drop(columns=['c_mtm', 'std', 's_mtm', f'CsMtmV3_{n}'], errors='ignore', inplace=True)

    return df

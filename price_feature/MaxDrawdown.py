def signal(*args):
    # MaxDrawdown indicator (close relative to the rolling high (drawdown proxy))
    # Formula: MaxDrawdown = CLOSE / rolling n-day peak of HIGH
    # Current close divided by the n-day rolling peak of high.
    # Values below 1 indicate an active drawdown; the further below 1, the deeper the pullback from the recent peak.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'Max_{n}'] = df['high'].rolling(n, min_periods=1).max()
    df[factor_name] = df['close'] / df[f'Max_{n}']
    df.drop(columns=[f'Max_{n}'], errors='ignore', inplace=True)

    return df

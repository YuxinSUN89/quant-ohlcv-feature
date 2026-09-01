eps = 1e-8


def signal(*args):
    # CostPriceMa indicator (volume-weighted average holding-cost line)
    # Formula: AMOV = VOLUME * (OPEN, CLOSE) / 2, AMV = SUM(AMOV, n) / SUM(VOLUME, n)
    # Volume-weighted (open+close)/2, moving-averaged over n periods — an estimate of the market's average recent holding cost.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['AMOV'] = df['volume'] * (df['open'] + df['close']) / 2
    df['AMV'] = df['AMOV'].rolling(window=n).sum() / (df['volume'] + eps).rolling(window=n).sum()
    df['Amv'] = df['close'] / df['AMV'] - 1
    df[factor_name] = df['Amv']
    df.drop(columns=['AMOV', 'AMV', 'Amv'], errors='ignore', inplace=True)

    return df

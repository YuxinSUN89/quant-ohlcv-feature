eps = 1e-8


def signal(*args):
    # Amv01 indicator (volume-weighted average price, min-max normalized)
    # Formula: AMOV = VOLUME*(OPEN+CLOSE)/2, AMV = SUM(AMOV,N)/SUM(VOLUME,N); Amv01 min-max normalizes AMV over n; n defaults to 13
    # AMV weights (open+close)/2 by volume, then scales the result to a 0-1 range over the lookback.
    # A value near 1 means the volume-weighted price is near its local high; near 0 means it is near its local low.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 13
    df['AMOV'] = df['volume'] * (df['open'] + df['close']) / 2
    df['AMV'] = df['AMOV'].rolling(n).sum() / (df['volume'] + eps).rolling(n).sum()
    df[f'Amv01_{n}'] = (df['AMV'] - df['AMV'].rolling(n).min()) / (df['AMV'].rolling(n).max() - df['AMV'].rolling(n).min())
    df[factor_name] = df[f'Amv01_{n}']
    df.drop(columns=['AMOV', 'AMV', f'Amv01_{n}'], errors='ignore', inplace=True)

    return df

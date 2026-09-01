def signal(*args):
    # CoppAtr indicator (Coppock Curve scaled by Average True Range)
    # Formula: CoppAtr = Copp factor * Atr factor, where Copp uses n1=n, n2=2n, m=n
    # Multiplies the Coppock momentum curve by ATR so the signal is weighted by prevailing volatility.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['RC'] = 100 * ((df['close'] - df['close'].shift(n)) / df['close'].shift(n) + (df['close'] - df['close'].shift(2 * n)) / df['close'].shift(2 * n))
    df['RC_mean'] = df['RC'].rolling(n, min_periods=1).mean()
    df['median'] = df['close'].rolling(window=n).mean()
    df['c1'] = df['high'] - df['low']  # HIGH-LOW
    df['c2'] = abs(df['high'] - df['close'].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df['c3'] = abs(df['low'] - df['close'].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df['TR'] = df[['c1', 'c2', 'c3']].max(axis=1)  # TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    df['_ATR'] = df['TR'].rolling(n, min_periods=1).mean()  # ATR=MA(TR,N)
    df['ATR'] = df['_ATR'] / df['median']
    df[f'CoppAtr_{n}'] = df['RC_mean'] * df['ATR']
    df[factor_name] = df[f'CoppAtr_{n}']
    df.drop(columns=['RC', 'RC_mean', 'median', 'c1', 'c2', 'c3', 'TR', '_ATR', 'ATR', f'CoppAtr_{n}'], errors='ignore', inplace=True)

    return df

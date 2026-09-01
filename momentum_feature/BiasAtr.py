def signal(*args):
    # BiasAtr indicator (Bias scaled by Average True Range)
    # Formula: BiasAtr = Bias * ATR
    # Multiplies the standard price-vs-moving-average bias by ATR.
    # Weights the bias reading up during high-volatility regimes and down during quiet ones.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'MA_{n}'] = df['close'].rolling(n).mean()
    df[f'Bias_{n}'] = (df["close"] - df[f'MA_{n}']) / df[f'MA_{n}']
    df['c1'] = df['high'] - df['low']  # HIGH-LOW
    df['c2'] = abs(df['high'] - df['close'].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df['c3'] = abs(df['low'] - df['close'].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df['TR'] = df[['c1', 'c2', 'c3']].max(axis=1)  # TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    df['_ATR'] = df['TR'].rolling(n, min_periods=1).mean()  # ATR=MA(TR,N)
    df['middle'] = df['close'].rolling(n, min_periods=1).mean()  # MIDDLE=MA(CLOSE,N)
    df[f'Atr_{n}'] = df['_ATR'] / (df['middle'] + 1e-8)
    df[f'BiasAtr_{n}'] = df[f'Bias_{n}'] * df[f'Atr_{n}']
    df[factor_name] = df[f'BiasAtr_{n}']
    df.drop(columns=[f'MA_{n}', f'Bias_{n}', 'c1', 'c2', 'c3', 'TR', '_ATR', 'middle', f'Atr_{n}', f'BiasAtr_{n}'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # G63 indicator (RSI-style up/down ratio, 6-period)
    # Formula: G63 = SMA(MAX(CLOSE-DELAY(CLOSE,1),0),6,1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),6,1)*100
    # Smoothed ratio of up-day gains to absolute price change over a 6-period window, scaled to 0-100 — a fast RSI variant.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['MAX_1'] = df['close'] - df['close'].shift(1)
    df['MAX_2'] = 0.0
    df['MAX'] = df[['MAX_1', 'MAX_2']].max(axis=1)
    df['SMA_1'] = df['MAX'].ewm(alpha=1.0 / 6, adjust=False).mean()
    df['ABS'] = (df['close'] - df['close'].shift(1)).abs()
    df['SMA_2'] = df['ABS'].ewm(alpha=1.0 / 6, adjust=False).mean()
    df['G63'] = df['SMA_1'] / df['SMA_2'] * 100
    df[factor_name] = df['G63']
    df.drop(columns=['MAX_1', 'MAX_2', 'MAX', 'SMA_1', 'ABS', 'SMA_2', 'G63'], errors='ignore', inplace=True)

    return df

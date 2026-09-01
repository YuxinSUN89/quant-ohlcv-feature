def signal(*args):
    # BollingV4 indicator (distance outside the Bollinger Bands)
    # Formula: If CLOSE > boll upper, distance = CLOSE - upper; if CLOSE < boll lower, distance = CLOSE - lower; else distance = 0
    # Zero while price sits inside the bands; otherwise the signed distance beyond the breached band.
    # Nonzero only during a Bollinger breakout, with magnitude proportional to how far price has broken out.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 20
    df['std'] = df['close'].rolling(n, min_periods=1).std()
    df['ma'] = df['close'].rolling(n, min_periods=1).mean()
    df['upper'] = df['ma'] + 1.0 * df['std']
    df['lower'] = df['ma'] - 1.0 * df['std']
    condition_0 = (df['close'] <= df['upper']) & (df['close'] >= df['lower'])
    condition_1 = df['close'] > df['upper']
    condition_2 = df['close'] < df['lower']
    df.loc[condition_0, 'distance'] = 0
    df.loc[condition_1, 'distance'] = df['close'] - df['upper']
    df.loc[condition_2, 'distance'] = df['close'] - df['lower']
    df[f'BollingV4_{n}'] = df['distance'] / (1e-8 + df['std'])
    df[factor_name] = df[f'BollingV4_{n}']
    df.drop(columns=['std', 'ma', 'upper', 'lower', f'BollingV4_{n}', 'distance'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # PctChgTrend indicator (lagged return relative to its own amplitude range)
    # Formula: PctChgTrend: pct_chg = CLOSE.pct_change(n).shift(1); trend = pct_chg / (MAX(HIGH,n) / MIN(LOW, n) - 1).shift(1)
    # The lagged n-day return, divided by the lagged n-day high/low amplitude.
    # Normalizes momentum by how wide the trading range was, so moves are compared on a like-for-like basis.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df['pct_chg'] = df['close'].pct_change(n).shift(1)
    high = df['high'].rolling(n, min_periods=1).max()
    low = df['low'].rolling(n, min_periods=1).min()
    df['pctchgtrend_1'] = (high / low - 1).shift(1)
    df['pctchgtrend_0'] = df['pct_chg'] / (df['pctchgtrend_1'] + 1e-8)
    df[f'pctchgtrend_6'] = df['pct_chg'] * abs(df['pctchgtrend_0'])
    df[factor_name] = df[f'pctchgtrend_6']
    df.drop(columns=['pct_chg', 'pctchgtrend_1', 'pctchgtrend_0', f'pctchgtrend_6', 'pct_chg'], errors='ignore', inplace=True)

    return df

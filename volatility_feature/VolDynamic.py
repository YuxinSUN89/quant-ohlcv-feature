def signal(*args):
    # VolDynamic indicator (Average True Range)
    # Formula: true_range = MAX(HIGH - LOW, abs(HIGH - PREV_CLOSE), abs(LOW - PREV_CLOSE)); atr = MA(true_range, n)
    # Standard ATR: the moving average of the true range (largest of high-low, |high-prior close|, |low-prior close|).
    # A baseline volatility measure — higher values mean wider, choppier bars.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['high-low'] = df['high'] - df['low']
    df['high-prev_close'] = abs(df['high'] - df['close'].shift(1))
    df['low-prev_close'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high-low', 'high-prev_close', 'low-prev_close']].max(axis=1)
    df['atr'] = df['true_range'].rolling(n).mean()
    df[f'DVF_{n}'] = (df['close'] - df['close'].shift(n)) / df['atr']
    df[factor_name] = df[f'DVF_{n}']
    df.drop(columns=['high-low', 'high-prev_close', 'low-prev_close', 'true_range', 'atr', f'DVF_{n}'], errors='ignore', inplace=True)

    return df

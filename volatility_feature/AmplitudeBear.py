def signal(*args):
    # AmplitudeBear indicator (downside amplitude from a lagged low)
    # Formula: AmplitudeBear = (MIN(MIN(CLOSE, OPEN), n).shift(1) - CLOSE) / CLOSE - 1
    # Gap between the current close and the lagged n-day low of min(close, open), relative to close.
    # More negative values indicate price has fallen further below its recent lagged floor.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    low = df[['close', 'open']].min(axis=1)
    low = low.rolling(n, min_periods=1).min()
    low = low.shift(1)
    df[f'amplitudebear_1'] = (low - df['close']) / (df['close'] + 1e-8)
    df[factor_name] = df[f'amplitudebear_1']
    df.drop(columns=[f'amplitudebear_1'], errors='ignore', inplace=True)

    return df

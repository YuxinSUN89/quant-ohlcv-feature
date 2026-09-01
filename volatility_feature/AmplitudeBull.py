def signal(*args):
    # AmplitudeBull indicator (upside amplitude from a lagged high)
    # Formula: AmplitudeBull = (MAX(MAX(CLOSE, OPEN), n).shift(1) - CLOSE) / CLOSE - 1
    # Gap between the current close and the lagged n-day high of max(close, open), relative to close.
    # More positive values indicate price has risen further above its recent lagged ceiling.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    high = df[['close', 'open']].max(axis=1)
    high = high.rolling(n, min_periods=1).max()
    high = high.shift(1)
    df[f'amplitudebull_1'] = (df['close'] - high) / (df['close'] + 1e-8)
    df[factor_name] = df[f'amplitudebull_1']
    df.drop(columns=[f'amplitudebull_1'], errors='ignore', inplace=True)

    return df

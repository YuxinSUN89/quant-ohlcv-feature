eps = 1e-8


def signal(*args):
    # AmplitudeOptimized indicator (amplitude normalized by trading value, lagged)
    # Formula: AmplitudeOptimized = MA(((HIGH / LOW - 1) / QUOTE_VOLUME).shift(), n)
    # n-day moving average of the prior day's (high/low - 1) amplitude divided by quote volume.
    # Lower values mean a given amount of range expansion required more trading value to produce — i.e. less efficient price movement.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['amplitudeoptimized_1'] = df['high'] / df['low'] - 1
    df['amplitudeoptimized_2'] = df['amplitudeoptimized_1'] / (df['quote_volume'] + eps)
    df['amplitudeoptimized_2'] = df['amplitudeoptimized_2'].shift()
    df[f'amplitudeoptimized_3'] = df['amplitudeoptimized_2'].rolling(n).mean()
    df[factor_name] = df[f'amplitudeoptimized_3']
    df.drop(columns=['amplitudeoptimized_1', 'amplitudeoptimized_2', f'amplitudeoptimized_3'], errors='ignore', inplace=True)

    return df

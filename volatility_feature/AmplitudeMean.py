eps = 1e-8


def signal(*args):
    # AmplitudeMean indicator (average daily amplitude)
    # Formula: Amplitude = (HIGH - LOW) / OPEN, averaged over n
    # Rolling n-day average of the day's (high-low)/open range.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['amplitudemean_1'] = (df['high'] - df['low'] + eps) / df['open'] - 1
    df[f'amplitudemean_2'] = df['amplitudemean_1'].rolling(n).mean()
    df[factor_name] = df[f'amplitudemean_2']
    df.drop(columns=['amplitudemean_1', f'amplitudemean_2'], errors='ignore', inplace=True)

    return df

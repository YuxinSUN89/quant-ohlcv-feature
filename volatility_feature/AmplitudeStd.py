eps = 1e-8


def signal(*args):
    # AmplitudeStd indicator (dispersion of daily amplitude)
    # Formula: Amplitude = (HIGH - LOW) / OPEN, std over n
    # Rolling n-day std of the day's (high-low)/open range.
    # Higher values mean the size of the daily trading range has been inconsistent recently.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['amplitudestd_1'] = (df['high'] - df['low'] + eps) / df['open'] - 1
    df[f'amplitudestd_2'] = df['amplitudestd_1'].rolling(n).std(ddof=0)
    df[factor_name] = df[f'amplitudestd_2']
    df.drop(columns=['amplitudestd_1', f'amplitudestd_2'], errors='ignore', inplace=True)

    return df

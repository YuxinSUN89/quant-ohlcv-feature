import pandas as pd


def signal(*args):
    # AmplitudeV2 indicator (amplitude measured from open/close extremes)
    # Formula: AmplitudeV2 = MAX(MAX(CLOSE, OPEN), n) / MIN(MIN(CLOSE, OPEN), n) - 1
    # Ratio of the n-day max of max(close, open) to the n-day min of min(close, open), minus 1.
    # A range measure that ignores wicks and only looks at where price actually opened/closed.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    high = df[['close', 'open']].max(axis=1)
    low = df[['close', 'open']].min(axis=1)
    high = pd.Series(high).rolling(n, min_periods=1).max()
    low = pd.Series(low).rolling(n, min_periods=1).min()
    df[f'amplitudev2_1'] = high / (low + 1e-8) - 1
    df[factor_name] = df[f'amplitudev2_1']
    df.drop(columns=[f'amplitudev2_1'], errors='ignore', inplace=True)

    return df

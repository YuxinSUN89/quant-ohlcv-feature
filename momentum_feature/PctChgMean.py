import pandas as pd


def signal(*args):
    # PctChgMean indicator (average daily return)
    # Formula: PCT_CHGMean = MA(CLOSE.pct_change(), n)
    # Rolling n-day mean of daily percentage returns.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    change = df['close'].pct_change()
    df[f'pctchgmean_1'] = pd.Series(change).rolling(n).mean()
    df[factor_name] = df[f'pctchgmean_1']
    df.drop(columns=[f'pctchgmean_1'], errors='ignore', inplace=True)

    return df

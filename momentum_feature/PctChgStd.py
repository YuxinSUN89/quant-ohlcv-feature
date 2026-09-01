import pandas as pd


def signal(*args):
    # PctChgStd indicator (dispersion of daily returns)
    # Formula: PCT_CHGStd = STD(CLOSE.pct_change(), n)
    # Rolling n-day standard deviation of daily percentage returns (same construction as Volatility.py).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    change = df['close'].pct_change()
    df[f'pctchgstd_1'] = pd.Series(change).rolling(n).std()
    df[factor_name] = df[f'pctchgstd_1']
    df.drop(columns=[f'pctchgstd_1'], errors='ignore', inplace=True)

    return df

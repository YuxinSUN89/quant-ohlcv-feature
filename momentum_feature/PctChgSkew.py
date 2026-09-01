import pandas as pd


def signal(*args):
    # PctChgSkew indicator (skewness of daily returns)
    # Formula: PctChgSkew = skew(CLOSE.pct_change(), n)
    # Rolling n-day skew of daily percentage returns.
    # Positive skew means occasional large up days; negative skew means occasional large down days.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    change = df['close'].pct_change()
    df[f'ZhangDieFuSkew_{n}'] = pd.Series(change).rolling(n).skew()
    df[factor_name] = df[f'ZhangDieFuSkew_{n}']
    df.drop(columns=[f'ZhangDieFuSkew_{n}'], errors='ignore', inplace=True)

    return df

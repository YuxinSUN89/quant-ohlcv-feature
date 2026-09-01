import numpy as np


eps = 1e-8


def signal(*args):
    # Rsj indicator (RSJ — ratio of up/down realized variance)
    # Formula: RV = SUM(return^2, N); RV+ = SUM(max(return,0)^2, N); RV- = SUM(min(return,0)^2, N)
    #          RSJ = (RV+ - RV-) / RV
    # Measures the asymmetry between upside and downside realized variance.
    # Positive values indicate right-skewed returns (more upside variance); negative indicate left-skewed.
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # calculate returns
    df['return'] = df['close'] / df['close'].shift(1) - 1

    # calculate RV
    df['pow_return'] = pow(df['return'], 2)
    df['rv'] = df['pow_return'].rolling(window=n, min_periods=1).sum()

    # calculate RV +/-
    df['positive_data'] = np.where(df['return'] > 0, df['return'], 0)
    df['negative_data'] = np.where(df['return'] < 0, df['return'], 0)
    df['pow_positive_data'] = pow(df['positive_data'], 2)
    df['pow_negetive_data'] = pow(df['negative_data'], 2)
    df['rv+'] = df['pow_positive_data'].rolling(window=n, min_periods=1).sum()
    df['rv-'] = df['pow_negetive_data'].rolling(window=n, min_periods=1).sum()

    # calculate RSJ
    df[factor_name] = (df['rv+'] - df['rv-']) / (df['rv'] + eps)

    # remove redundant columns
    del df['return'], df['rv'], df['positive_data'], df['negative_data']
    del df['rv+'], df['rv-'], df['pow_positive_data'], df['pow_negetive_data']
    del df['pow_return']

    return df

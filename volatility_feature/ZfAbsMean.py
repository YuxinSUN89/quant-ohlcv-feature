"""
Strategy Sharing Session
Position Management Framework

Copyright reserved.

This code is for personal learning use only. Copying, modification, or commercial use without authorization is prohibited.
"""
import numpy as np


def signal(*args):
    df = args[0]
    n = args[1]
    factor_name = args[2]

    df['avg_price'] = (df['close'] + df['high'] + df['low']) / 3

    df['price_change'] = df['avg_price'].pct_change()
    df['amplitude'] = (df['high'] - df['low']) / df['open']
    df['amplitude'] = np.where(df['price_change'] > 0, df['amplitude'], 0)
    df['amplitude_mean'] = df['amplitude'].rolling(n, min_periods=1).mean()

    df[factor_name] = df['amplitude_mean'].rolling(n, min_periods=1).rank(ascending=True, pct=True)

    del df['avg_price']
    del df['price_change']
    del df['amplitude']
    del df['amplitude_mean']

    return df

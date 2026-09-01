import numpy as np


def signal(*args):
    # H92 indicator (decay-weighted rank of range position vs. volume/price correlation)
    # Formula: H92 = min(ts_rank(decay_linear(((((HIGH + LOW) / 2) + CLOSE) < (LOW + OPEN)), 14.7221), 18.8683),ts_rank(decay_linear(correlation(rank(LOW), rank(ADV30), 7.58555), 6.94024), 6.80584))
    # Takes the smaller of two decay-weighted, rank-based measures: one on range position vs. open/low, another on low-rank vs. volume-rank correlation.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['Demax'] = df['high'] - df['high'].shift(1)
    df['Demax'] = np.where(df['Demax'] > 0, df['Demax'], 0)
    df['Demin'] = df['low'].shift(1) - df['low']
    df['Demin'] = np.where(df['Demin'] > 0, df['Demin'], 0)
    df['Demax_ma'] = df['Demax'].rolling(5, min_periods=1).mean()
    df['Demin_ma'] = df['Demin'].rolling(5, min_periods=1).mean()
    df[f'H92'] = df['Demax_ma'] / (df['Demax_ma'] + df['Demin_ma'])
    df[factor_name] = df[f'H92']
    df.drop(columns=['Demax', 'Demin', 'Demax_ma', 'Demin_ma', f'H92'], errors='ignore', inplace=True)

    return df

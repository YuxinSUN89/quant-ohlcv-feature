import pandas as pd

eps = 1e-8


def signal(*args):
    # H43 indicator (rank-momentum of relative turnover and price change)
    # Formula: H43 = (ts_rank((AMOUNT / ADV20), 20) * ts_rank((-1 * delta(CLOSE, 7)), 8))
    # Product of the 20-day time-series rank of (trading value / 20-day average volume) and the 8-day rank of negative 7-day price change.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H43_to_tsrank_1'] = df['quote_volume'] / (df['quote_volume'] + eps).rolling(20).mean()
    df['H43_to_tsrank_2'] = -1*df['close'].diff(7)
    df['H43_tsrank_1'] = df['H43_to_tsrank_1'].rolling(20, min_periods=1).apply( lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['H43_tsrank_2'] = df['H43_to_tsrank_2'].rolling(8, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['H43'] = df['H43_tsrank_1'] * df['H43_tsrank_2']
    df[factor_name] = df['H43']
    df.drop(columns=['H43_to_tsrank_1', 'H43_to_tsrank_2', 'H43_tsrank_1', 'H43_tsrank_2', 'H43'], errors='ignore', inplace=True)

    return df

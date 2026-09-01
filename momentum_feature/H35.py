import pandas as pd


def signal(*args):
    # H35 indicator (rank-momentum blend of volume, range position and returns)
    # Formula: H35 = ((ts_rank(VOLUME, 32) * (1 - ts_rank(((CLOSE + HIGH) - LOW), 16))) * (1 - ts_rank(RETURNS, 32)))
    # Multiplies the time-series rank of volume by (1 - rank of (close+high-low)) by (1 - rank of returns), each over their own window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H35_to_rank_1'] = df['quote_volume']
    df['H35_to_rank_2'] = (df['close'] + df['high']) - df['low']
    df['H35_to_rank_3'] = (df['close'] - df['close'].shift()) / df['close'].shift()
    df['H35_rank_1'] = df['H35_to_rank_1'].rolling(32, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['H35_rank_2'] = df['H35_to_rank_2'].rolling(16, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['H35_rank_3'] = df['H35_to_rank_3'].rolling(32, min_periods=1).apply(lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['H35'] = df['H35_rank_1'] * (1 - df['H35_rank_2']) * (1 - df['H35_rank_3'])
    df[factor_name] = df['H35']
    df.drop(columns=['H35_to_rank_1', 'H35_to_rank_2', 'H35_to_rank_3', 'H35_rank_1', 'H35_rank_2', 'H35_rank_3', 'H35'], errors='ignore', inplace=True)

    return df

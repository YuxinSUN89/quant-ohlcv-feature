import numpy as np


def signal(*args):
    # G69 indicator (directional-movement balance (ADX raw DTM/DBM style))
    # Formula: G69 = (SUM(DTM,20)>SUM(DBM,20) ？ (SUM(DTM,20)-SUM(DBM,20))/SUM(DTM,20) ： (SUM(DTM,20)=SUM(DBM,20) ？0：(SUM(DTM,20)-SUM(DBM,20))/SUM(DBM,20)))
    # Ratio of the 20-day imbalance between up-moves (DTM) and down-moves (DBM) to whichever side dominates.
    # Positive values indicate up-moves have dominated over the window; negative values indicate down-moves have dominated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G69_DTM_MAX1'] = df['high'] - df['open']
    df['G69_DTM_MAX2'] = df['open'].diff()
    df['G69_DTM'] = np.where((df['open'] <= df['open'].shift()), 0, df[['G69_DTM_MAX1', 'G69_DTM_MAX2']].max(axis=1))
    df['G69_DBM_MAX1'] = df['open'] - df['low']
    df['G69_DBM_MAX2'] = df['open'].diff()
    df['G69_DBM'] = np.where((df['open'] >= df['open'].shift()), 0, df[['G69_DBM_MAX1', 'G69_DBM_MAX2']].max(axis=1))
    df['G69_SUM_DTM20'] = df['G69_DTM'].rolling(20, min_periods=1).sum()
    df['G69_SUM_DBM20'] = df['G69_DBM'].rolling(20, min_periods=1).sum()
    df['G69_0'] = np.where((df['G69_SUM_DTM20'] == df['G69_SUM_DBM20']), 0, (df['G69_SUM_DTM20'] - df['G69_SUM_DBM20']) / df['G69_SUM_DBM20'])
    df['G69_1'] = (df['G69_SUM_DTM20'] - df['G69_SUM_DBM20']) / df['G69_SUM_DTM20']
    df['G69'] = np.where((df['G69_SUM_DTM20'] > df['G69_SUM_DBM20']), df['G69_1'], df['G69_0'])
    df[factor_name] = df['G69']
    df.drop(columns=['G69_DTM_MAX1', 'G69_DTM_MAX2', 'G69_DTM', 'G69_DBM_MAX1', 'G69_DBM_MAX2', 'G69_DBM', 'G69_SUM_DTM20', 'G69_SUM_DBM20', 'G69_0', 'G69_1', 'G69'], errors='ignore', inplace=True)

    return df

import pandas as pd

eps = 1e-8


def signal(*args):
    # G85 indicator (rank-momentum of relative volume times rank-momentum of price change)
    # Formula: G85 = TSRANK((VOLUME / MEAN(VOLUME,20)), 20) * TSRANK((-1 * DELTA(CLOSE, 7)), 8)
    # Product of the 20-day time-series rank of relative volume and the 8-day time-series rank of negative 7-day price change.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    param = [20, 20, -1, 7, 8]
    s_left = df['volume'] / (df['volume'] + eps).rolling(param[0], min_periods=1).mean()
    s_left = s_left.rolling(param[1], min_periods=1).apply( lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    s_right = param[2] * df['close'].diff(param[3])
    s_right = s_right.rolling(param[4], min_periods=1).apply( lambda x: pd.Series(x).rank(pct=True, method='first').iloc[-1])
    df['G85'] = s_left * s_right
    df[factor_name] = df['G85']
    df.drop(columns=['G85'], errors='ignore', inplace=True)

    return df

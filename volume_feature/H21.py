eps = 1e-8


def signal(*args):
    # H21 indicator (trend-exhaustion / relative-volume switch)
    # Formula: H21 = ((((sum(CLOSE, 8) / 8) + stddev(CLOSE, 8)) < (sum(CLOSE, 2) / 2)) ? (-1 * 1): (((sum(CLOSE, 2) / 2) < ((sum(CLOSE, 8) / 8) - stddev(CLOSE, 8))) ? 1: (((1 < (VOLUME / ADV20)) | | ( (VOLUME / ADV20) == 1)) ? 1: (-1 * 1))))
    # Detects whether a short average has moved too far above or below an 8-day average (signalling exhaustion), otherwise falls back to a relative-volume-vs-20-day-average check.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['a'] = df['close'].rolling(8, min_periods=1).sum()/8+df['close'].rolling(8, min_periods=1).std()
    df['b'] = df['close'].rolling(2, min_periods=1).sum()/2
    df['c'] = df['b']
    df['d'] = df['close'].rolling(8, min_periods=1).sum()/8
    df['e'] = df['close'].rolling(8, min_periods=1).std()
    df['f'] = df['quote_volume']/ (df['quote_volume'] + eps).rolling(20, min_periods=1).mean()
    df['H21'] = df.apply(lambda x: -1 if x['a'] < x['b'] else 1 if x['c'] < (x['d']-x['e']) else 1 if x['f'] >= 1 else -1, axis=1)
    df[factor_name] = df['H21']
    df.drop(columns=['a', 'b', 'c', 'd', 'e', 'f', 'H21'], errors='ignore', inplace=True)

    return df

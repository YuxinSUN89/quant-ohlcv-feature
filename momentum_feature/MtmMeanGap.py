eps = 1e-8


def signal(*args):
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # MtmMeanGap indicator (MTM mean / gap factor)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; GAP = MA(1 - |CLOSE-OPEN|/(HIGH-LOW), N)
    #          result = MA(MTM, N) / GAP
    # GAP measures candle body proportion relative to the range (low = doji/indecision candles).
    # Dividing momentum mean by GAP boosts signal when candles show clear directional intent.
    df['mtm'] = df['close'] / df['close'].shift(n) - 1

    df['_g']  = 1 - abs((df['close'] - df['open'])/(df['high'] - df['low'] + eps))
    df['gap'] = df['_g'].rolling(window=n, min_periods=1).mean()

    df[factor_name] = df['mtm'].rolling(window=n, min_periods=1).mean()/(df['gap'] + eps)

    del df['mtm']
    del df['_g']
    del df['gap']

    return df

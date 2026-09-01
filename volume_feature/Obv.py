eps = 1e-8


def signal(*args):
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # OBV indicator (CLV-weighted On Balance Volume variant)
    # Formula: CLV = (2*CLOSE - LOW - HIGH) / (HIGH - LOW); VA = CLV * VOLUME
    #          OBV = SUM(VA, N); normalized as OBV / MA(OBV, N)
    # Weights volume by the CLV factor, which reflects where the close falls within the high-low range.
    # CLV > 0 means close is above midpoint (accumulation); CLV < 0 means below midpoint (distribution).
    # Values above 1 indicate above-average buying pressure; below 1 indicate selling pressure.
    df['_va'] = (df['close'] - df['low'] - (df['high'] - df['close'])) / (df['high'] - df['low'] + eps) * df['volume']
    df['_obv'] = df['_va'].rolling(n).sum()

    # ref = ma.shift(n)  # MADisplaced=REF(MA_CLOSE,M)

    df[factor_name] = df['_obv'] / df['_obv'].rolling(n).mean()  # normalize

    del df['_va']
    del df['_obv']

    return df

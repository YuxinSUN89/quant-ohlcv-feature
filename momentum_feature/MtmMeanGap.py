def signal(df, n, factor_name, config):
    eps = config.eps
    # MtmMeanGap indicator (MTM mean / gap factor)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; GAP = MA(1 - |CLOSE-OPEN|/(HIGH-LOW), N)
    #          result = MA(MTM, N) / GAP
    # GAP measures candle body proportion relative to the range (low = doji/indecision candles).
    # Dividing momentum mean by GAP boosts signal when candles show clear directional intent.
    df["mtm"] = df["close"] / df["close"].shift(n) - 1

    df["_g"] = 1 - abs((df["close"] - df["open"]) / (df["high"] - df["low"] + eps))
    df["gap"] = df["_g"].rolling(window=n, min_periods=config.min_periods).mean()

    df[factor_name] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean() / (df["gap"] + eps)

    return df

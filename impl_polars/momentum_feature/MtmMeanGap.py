import polars as pl


def signal(df, n, factor_name, config):
    eps = config.eps
    # MtmMeanGap indicator (MTM mean / gap factor)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; GAP = MA(1 - |CLOSE-OPEN|/(HIGH-LOW), N)
    #          result = MA(MTM, N) / GAP
    # GAP measures candle body proportion relative to the range (low = doji/indecision candles).
    # Dividing momentum mean by GAP boosts signal when candles show clear directional intent.
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))

    df = df.with_columns(pl.Series("_g", 1 - abs((df["close"] - df["open"]) / (df["high"] - df["low"] + eps))))
    df = df.with_columns(pl.Series("gap", df["_g"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(
        pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods) / (df["gap"] + eps))
    )

    return df

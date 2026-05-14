import polars as pl


def signal(df, n, factor_name, config):
    # Vao indicator (Volume Analysis Oscillator)
    # Formula: WV = VOLUME * (CLOSE - 0.5*HIGH - 0.5*LOW); VAO = WV + REF(WV, 1)
    #          result = MA(VAO, N) - MA(VAO, 3N)
    # Weights volume by how far the close is from the midpoint of the candle (above midpoint = buying,
    # below = selling). The difference of short and long MAs acts as an oscillator around zero.
    # Positive values indicate net buying pressure; negative values indicate selling pressure.
    wv = df["volume"] * (df["close"] - 0.5 * df["high"] - 0.5 * df["low"])
    _vao = wv + wv.shift(1)
    vao_ma1 = _vao.rolling_mean(n, min_samples=config.min_periods)
    vao_ma2 = _vao.rolling_mean(int(3 * n), min_samples=config.min_periods)

    df = df.with_columns(pl.Series(factor_name, vao_ma1 - vao_ma2))

    return df

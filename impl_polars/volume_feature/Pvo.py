import polars as pl


def signal(df, n, factor_name, config):
    # Pvo indicator (Percentage Volume Oscillator)
    # Formula: EMA1 = EMA(VOLUME, N); EMA2 = EMA(VOLUME, 2N)
    #          PVO = (EMA1 - EMA2) / EMA2
    # Measures the percentage difference between short-term and long-term volume EMAs.
    # Positive values indicate short-term volume is above the longer-term average (volume surge);
    # negative values indicate declining volume relative to the trend.
    df = df.with_columns(pl.Series("emap_1", df["volume"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("emap_2", df["volume"].ewm_mean(span=n * 2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, (df["emap_1"] - df["emap_2"]) / df["emap_2"]))

    df = df.drop("emap_1")
    df = df.drop("emap_2")

    return df

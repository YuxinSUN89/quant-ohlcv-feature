import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Tema_v2 indicator (Close vs longer-period TEMA, percentage)
    # Formula: TEMA = TEMA(CLOSE, 2N); result = 100 * (CLOSE - TEMA) / (TEMA + eps)
    # Measures the percentage deviation of close from its 2N-period Triple Exponential MA.
    # Uses a longer window (2N) than the standard TEMA for a smoother trend baseline.
    # Positive values indicate close is above TEMA (upward momentum); negative below.
    eps = config.eps
    df = df.with_columns(pl.Series("TEMA", ta.TEMA(df["close"], timeperiod=2 * n)))
    df = df.with_columns(pl.Series(factor_name, 100 * (df["close"] - df["TEMA"]) / (df["TEMA"] + eps)))

    df = df.drop("TEMA")

    return df

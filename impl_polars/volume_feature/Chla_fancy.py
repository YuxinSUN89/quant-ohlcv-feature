import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Chla_fancy indicator (CLV-weighted Quote Volume rolling sum)
    # Formula: CLV = (2*CLOSE - HIGH - LOW) / (HIGH - LOW); CHLA = CLV * QUOTE_VOLUME
    #          result = SUM(CHLA, N)
    # Weights quote volume by the CLV factor (close position within the candle range).
    # Positive CLV (close near high) contributes positive volume; negative CLV (close near low)
    # contributes negative volume. Rolling sum reflects accumulated buying/selling pressure.
    df = df.with_columns(pl.Series("divnum", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("divnum", df["divnum"].replace(0, np.nan)))
    df = df.with_columns(
        pl.Series("temp", (2 * df["close"] - df["high"] - df["low"]) / df["divnum"] * df["quote_volume"])
    )
    df = df.with_columns(pl.Series(factor_name, df["temp"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.drop(["divnum", "temp"])

    return df

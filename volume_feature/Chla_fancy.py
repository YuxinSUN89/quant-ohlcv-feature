import numpy as np


def signal(df, n, factor_name, config):
    # Chla_fancy indicator (CLV-weighted Quote Volume rolling sum)
    # Formula: CLV = (2*CLOSE - HIGH - LOW) / (HIGH - LOW); CHLA = CLV * QUOTE_VOLUME
    #          result = SUM(CHLA, N)
    # Weights quote volume by the CLV factor (close position within the candle range).
    # Positive CLV (close near high) contributes positive volume; negative CLV (close near low)
    # contributes negative volume. Rolling sum reflects accumulated buying/selling pressure.
    df["divnum"] = df["high"] - df["low"]
    df["divnum"] = df["divnum"].replace(0, np.nan)
    df["temp"] = (2 * df["close"] - df["high"] - df["low"]) / df["divnum"] * df["quote_volume"]
    df[factor_name] = df["temp"].rolling(n, min_periods=config.min_periods).sum()

    del df["divnum"], df["temp"]

    return df

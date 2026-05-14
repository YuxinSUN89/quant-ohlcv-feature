import numpy as np
import polars as pl


def _rolling_mean_np(values, window, min_periods):
    arr = np.asarray(values, dtype=float)
    out = np.full(len(arr), np.nan)
    min_p = min_periods or 1
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        w = arr[start : i + 1]
        valid = w[~np.isnan(w)]
        if len(valid) < min_p:
            continue
        out[i] = valid.mean()
    return out


def signal(df, n, factor_name, config):
    # A price-volume indicator describing the difficulty of price breakouts
    # A certain price movement is caused by volume changes; if a certain price movement requires more volume, it indicates the asset is harder to control
    df = df.with_columns(pl.Series("close_shift", df["close"].shift(n)))
    df = df.with_columns(pl.Series("volume_shift", df["volume"].shift(n)))
    # Numerical sensitivity note:
    # PriceVolumeResist is sensitive to tiny residuals in the shifted rolling means and in
    # near-zero volume_ratio values. Those edge cases can flip between signed zero, tiny finite
    # values, and inf, so we use numpy rolling means to stay closer to pandas behaviour.
    close_shift_mean = pl.Series(_rolling_mean_np(df["close_shift"].to_numpy(), n, config.min_periods))
    volume_shift_mean = pl.Series(_rolling_mean_np(df["volume_shift"].to_numpy(), n, config.min_periods))
    df = df.with_columns(pl.Series("close_ratio", (df["close"] - close_shift_mean).abs() / (df["close_shift"] + config.eps)))
    df = df.with_columns(pl.Series("volume_ratio", (df["volume"] - volume_shift_mean) / (df["volume_shift"] + config.eps)))

    df = df.with_columns(pl.Series("angle", df["close_ratio"] * df["volume_ratio"]))

    condition = df["angle"] < 0  # price and volume move in opposite directions, breakout is effortless, set to inf
    df = df.with_columns(pl.lit(1).alias("direction"))
    df = df.with_columns(pl.lit(1).alias("adj"))
    df = df.with_columns(pl.when(condition).then(-1).otherwise(pl.col("direction")).alias("direction"))
    df = df.with_columns(pl.when(condition).then(np.inf).otherwise(pl.col("adj")).alias("adj"))

    df = df.with_columns(pl.Series(factor_name, df["close_ratio"] / df["volume_ratio"] * df["direction"] * df["adj"]))
    df = df.with_columns(pl.Series(factor_name, df[factor_name] / n))

    df = df.drop(["close_shift", "volume_shift", "close_ratio", "volume_ratio", "angle", "direction", "adj"])

    return df

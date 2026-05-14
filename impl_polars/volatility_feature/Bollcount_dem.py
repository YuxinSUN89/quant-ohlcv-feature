import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Bollcount_dem indicator (DeMarker overbought/oversold count)
    # Formula: Demax = MAX(HIGH - REF(HIGH,1), 0); Demin = MAX(REF(LOW,1) - LOW, 0)
    #          DeMarker = MA(Demax,N) / (MA(Demax,N) + MA(Demin,N))
    #          count = +1 if DeMarker > 0.7 (overbought), -1 if DeMarker < 0.3 (oversold), else 0
    #          result = SUM(count, N)
    # Uses the DeMarker indicator to count overbought (+1) and oversold (-1) periods over N bars.
    # Positive rolling sum indicates sustained overbought conditions; negative indicates oversold.
    # Boll_Count
    df = df.with_columns(pl.Series("Demax", df["high"].diff()))
    df = df.with_columns(pl.Series("Demax", np.where(df["Demax"].fill_null(0) > 0, df["Demax"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("Demin", df["low"].shift(1) - df["low"]))
    df = df.with_columns(pl.Series("Demin", np.where(df["Demin"].fill_null(0) > 0, df["Demin"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("Ma_Demax", df["Demax"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("Ma_Demin", df["Demin"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("Demaker", df["Ma_Demax"] / (df["Ma_Demax"] + df["Ma_Demin"])))
    df = df.with_columns(pl.col("Demaker").fill_nan(None).alias("Demaker"))

    df = df.with_columns(pl.lit(0).alias("count"))
    df = df.with_columns(pl.when(df["Demaker"] > 0.7).then(1).otherwise(pl.col("count")).alias("count"))
    df = df.with_columns(pl.when(df["Demaker"] < 0.3).then(-1).otherwise(pl.col("count")).alias("count"))
    df = df.with_columns(pl.Series(factor_name, df["count"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.drop(["Demax", "Demin", "Ma_Demax", "Ma_Demin", "Demaker", "count"])

    return df

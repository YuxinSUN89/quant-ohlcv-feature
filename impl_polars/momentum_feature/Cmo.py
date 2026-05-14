import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Cmo
    eps = config.eps
    # MAX(CLOSE-REF(CLOSE,1), 0
    df = df.with_columns(
        pl.Series(
            "max_su", np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0)
        ).fill_nan(None)
    )
    # SU=SUM(MAX(CLOSE-REF(CLOSE,1),0),N)
    df = df.with_columns(pl.Series("sum_su", df["max_su"].rolling_sum(n, min_samples=config.min_periods)))
    # MAX(REF(CLOSE,1)-CLOSE,0)
    df = df.with_columns(
        pl.Series(
            "max_sd", np.where(df["close"].shift(1) > df["close"], df["close"].shift(1) - df["close"], 0)
        ).fill_nan(None)
    )
    # SD=SUM(MAX(REF(CLOSE,1)-CLOSE,0),N)
    df = df.with_columns(pl.Series("sum_sd", df["max_sd"].rolling_sum(n, min_samples=config.min_periods)))
    # CMO=(SU-SD)/(SU+SD)*100
    df = df.with_columns(
        pl.Series(factor_name, (df["sum_su"] - df["sum_sd"]) / (df["sum_su"] + df["sum_sd"] + eps) * 100)
    )

    # delete extra columns
    df = df.drop(["max_su", "sum_su", "max_sd", "sum_sd"])

    return df

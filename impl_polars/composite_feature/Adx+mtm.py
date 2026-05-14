import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Adx+mtm indicator (DI+ directional strength × EMA-smoothed momentum)
    # Formula: PDM = positive directional movement (high gain only when larger than low gain)
    #          DI+ = SUM(PDM,N) / SUM(TR,N)  (positive directional indicator)
    #          MTM = MA(CLOSE/REF(CLOSE,N) - 1, N)  (rolling mean of N-period returns)
    #          result = DI+ * MTM
    # Composite of upward directional strength (DI+) and price momentum.
    # High positive values indicate strong upward trend with sustained momentum.
    df = df.with_columns(
        pl.Series("max_high", np.where(df["high"] > df["high"].shift(1), df["high"] - df["high"].shift(1), 0)).fill_nan(
            None
        )
    )

    df = df.with_columns(
        pl.Series("max_low", np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("XPDM", np.where(df["max_high"] > df["max_low"], df["high"] - df["high"].shift(1), 0)).fill_nan(None)
    )
    df = df.with_columns(pl.Series("PDM", df["XPDM"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series("c1", abs(df["high"] - df["low"])))
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"])))
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"])))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))

    df = df.with_columns(pl.Series("TR_sum", df["TR"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("DI+", df["PDM"] / (df["TR_sum"] + config.eps)))

    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("mtm_rolling", df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series(factor_name, df["DI+"] * df["mtm_rolling"]))

    df = df.drop(["max_high", "max_low", "XPDM", "PDM", "mtm", "mtm_rolling", "c1", "c2", "c3", "TR", "TR_sum", "DI+"])

    return df

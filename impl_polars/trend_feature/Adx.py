import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
    """
    N1=14
    MAX_HIGH=IF(HIGH>REF(HIGH,1),HIGH-REF(HIGH,1),0)
    MAX_LOW=IF(REF(LOW,1)>LOW,REF(LOW,1)-LOW,0)
    XPDM=IF(MAX_HIGH>MAX_LOW,HIGH-REF(HIGH,1),0)
    PDM=SUM(XPDM,N1)
    XNDM=IF(MAX_LOW>MAX_HIGH,REF(LOW,1)-LOW,0)
    NDM=SUM(XNDM,N1)
    TR=MAX([ABS(HIGH-LOW),ABS(HIGH-CLOSE),ABS(LOW-CLOSE)])
    TR=SUM(TR,N1)
    DI+=PDM/TR
    DI-=NDM/TR
    The DI+ and DI- indicators in the ADX calculation use the differences in consecutive
    daily highs and lows to reflect price trend direction. A buy signal is generated when
    DI+ crosses above DI-; a sell signal when DI+ crosses below DI-.
    """
    # MAX_HIGH=IF(HIGH>REF(HIGH,1),HIGH-REF(HIGH,1),0)
    df = df.with_columns(
        pl.Series("max_high", np.where(df["high"] > df["high"].shift(1), df["high"] - df["high"].shift(1), 0)).fill_nan(
            None
        )
    )
    # MAX_LOW=IF(REF(LOW,1)>LOW,REF(LOW,1)-LOW,0)
    df = df.with_columns(
        pl.Series("max_low", np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)).fill_nan(None)
    )
    # XPDM=IF(MAX_HIGH>MAX_LOW,HIGH-REF(HIGH,1),0)
    df = df.with_columns(
        pl.Series("XPDM", np.where(df["max_high"] > df["max_low"], df["high"] - df["high"].shift(1), 0)).fill_nan(None)
    )
    # PDM=SUM(XPDM,N1)
    df = df.with_columns(pl.Series("PDM", df["XPDM"].rolling_sum(n, min_samples=config.min_periods)))
    # XNDM=IF(MAX_LOW>MAX_HIGH,REF(LOW,1)-LOW,0)
    df = df.with_columns(
        pl.Series("XNDM", np.where(df["max_low"] > df["max_high"], df["low"].shift(1) - df["low"], 0)).fill_nan(None)
    )
    # NDM=SUM(XNDM,N1)
    df = df.with_columns(pl.Series("NDM", df["XNDM"].rolling_sum(n, min_samples=config.min_periods)))
    # ABS(HIGH-LOW)
    df = df.with_columns(pl.Series("c1", abs(df["high"] - df["low"])))
    # ABS(HIGH-CLOSE)
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"])))
    # ABS(LOW-CLOSE)
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"])))
    # TR=MAX([ABS(HIGH-LOW),ABS(HIGH-CLOSE),ABS(LOW-CLOSE)])
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    # TR=SUM(TR,N1)
    df = df.with_columns(pl.Series("TR_sum", df["TR"].rolling_sum(n, min_samples=config.min_periods)))
    # DI+=PDM/TR
    df = df.with_columns(pl.Series("DI+", df["PDM"] / df["TR"]))
    # DI-=NDM/TR
    df = df.with_columns(pl.Series("DI-", df["NDM"] / df["TR"]))

    df = df.with_columns(pl.Series(f"ADX_DI+_bh_{n}", df["DI+"].shift(1)))
    df = df.with_columns(pl.Series(f"ADX_DI-_bh_{n}", df["DI-"].shift(1)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, (df["PDM"] + df["NDM"]) / df["TR"]))

    # remove intermediate data
    df = df.drop("max_high")
    df = df.drop("max_low")
    df = df.drop("XPDM")
    df = df.drop("PDM")
    df = df.drop("XNDM")
    df = df.drop("NDM")
    df = df.drop("c1")
    df = df.drop("c2")
    df = df.drop("c3")
    df = df.drop("TR")
    df = df.drop("TR_sum")
    df = df.drop(["DI+", "DI-"])

    return df

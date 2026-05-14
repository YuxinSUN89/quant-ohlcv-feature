import polars as pl


def signal(df, n, factor_name, config):
    # PMO indicator
    """
    N1=10
    N2=40
    N3=20
    ROC=(CLOSE-REF(CLOSE,1))/REF(CLOSE,1)*100
    ROC_MA=DMA(ROC,2/N1)
    ROC_MA10=ROC_MA*10
    PMO=DMA(ROC_MA10,2/N2)
    PMO_SIGNAL=DMA(PMO,2/(N3+1))
    PMO is the double-smoothed (moving average) version of the ROC indicator. Unlike SROC
    (which smooths price first then computes ROC), PMO computes ROC first and then smooths it.
    A larger PMO (above 0) indicates a stronger uptrend; a smaller PMO (below 0) indicates
    a stronger downtrend. Buy/sell signals are generated when PMO crosses above/below its signal line.
    """
    df = df.with_columns(pl.Series("ROC", (df["close"] - df["close"].shift(1)) / (df["close"].shift(1) + config.eps) * 100))
    df = df.with_columns(pl.Series("ROC_MA", df["ROC"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ROC_MA10", df["ROC_MA"] * 10))
    df = df.with_columns(pl.Series("PMO", df["ROC_MA10"].rolling_mean(4 * n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["PMO"].rolling_mean(2 * n, min_samples=config.min_periods)))

    df = df.drop("ROC")
    df = df.drop("ROC_MA")
    df = df.drop("ROC_MA10")
    df = df.drop("PMO")

    return df

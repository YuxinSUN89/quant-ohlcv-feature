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
    df["ROC"] = (df["close"] - df["close"].shift(1)) / df["close"].shift(1) * 100
    df["ROC_MA"] = df["ROC"].rolling(n, min_periods=config.min_periods).mean()
    df["ROC_MA10"] = df["ROC_MA"] * 10
    df["PMO"] = df["ROC_MA10"].rolling(4 * n, min_periods=config.min_periods).mean()
    df[factor_name] = df["PMO"].rolling(2 * n, min_periods=config.min_periods).mean()

    del df["ROC"]
    del df["ROC_MA"]
    del df["ROC_MA10"]
    del df["PMO"]

    return df

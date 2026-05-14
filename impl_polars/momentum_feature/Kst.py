import polars as pl


def signal(df, n, factor_name, config):
    # KST indicator
    """
    ROC_MA1=MA(CLOSE-REF(CLOSE,10),10)
    ROC_MA2=MA(CLOSE -REF(CLOSE,15),10)
    ROC_MA3=MA(CLOSE -REF(CLOSE,20),10)
    ROC_MA4=MA(CLOSE -REF(CLOSE,30),10)
    KST_IND=ROC_MA1+ROC_MA2*2+ROC_MA3*3+ROC_MA4*4
    KST=MA(KST_IND,9)
    KST combines ROC indicators of different time lengths. Buy/sell signals are generated
    when KST crosses above/below 0.
    """
    df = df.with_columns(pl.Series("ROC1", df["close"] - df["close"].shift(n)))
    df = df.with_columns(pl.Series("ROC_MA1", df["ROC1"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ROC2", df["close"] - df["close"].shift(int(n * 1.5))))
    df = df.with_columns(pl.Series("ROC_MA2", df["ROC2"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ROC3", df["close"] - df["close"].shift(int(n * 2))))
    df = df.with_columns(pl.Series("ROC_MA3", df["ROC3"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ROC4", df["close"] - df["close"].shift(int(n * 3))))
    df = df.with_columns(pl.Series("ROC_MA4", df["ROC4"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series("KST_IND", df["ROC_MA1"] + df["ROC_MA2"] * 2 + df["ROC_MA3"] * 3 + df["ROC_MA4"] * 4)
    )
    df = df.with_columns(pl.Series("KST", df["KST_IND"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["KST_IND"] / df["KST"]))

    df = df.drop("ROC1")
    df = df.drop("ROC_MA1")
    df = df.drop("ROC2")
    df = df.drop("ROC_MA2")
    df = df.drop("ROC3")
    df = df.drop("ROC_MA3")
    df = df.drop("ROC4")
    df = df.drop("ROC_MA4")
    df = df.drop("KST_IND")
    df = df.drop("KST")

    return df

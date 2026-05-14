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
    df["ROC1"] = df["close"] - df["close"].shift(n)
    df["ROC_MA1"] = df["ROC1"].rolling(n, min_periods=config.min_periods).mean()
    df["ROC2"] = df["close"] - df["close"].shift(int(n * 1.5))
    df["ROC_MA2"] = df["ROC2"].rolling(n, min_periods=config.min_periods).mean()
    df["ROC3"] = df["close"] - df["close"].shift(int(n * 2))
    df["ROC_MA3"] = df["ROC3"].rolling(n, min_periods=config.min_periods).mean()
    df["ROC4"] = df["close"] - df["close"].shift(int(n * 3))
    df["ROC_MA4"] = df["ROC4"].rolling(n, min_periods=config.min_periods).mean()
    df["KST_IND"] = df["ROC_MA1"] + df["ROC_MA2"] * 2 + df["ROC_MA3"] * 3 + df["ROC_MA4"] * 4
    df["KST"] = df["KST_IND"].rolling(n, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = df["KST_IND"] / df["KST"]

    del df["ROC1"]
    del df["ROC_MA1"]
    del df["ROC2"]
    del df["ROC_MA2"]
    del df["ROC3"]
    del df["ROC_MA3"]
    del df["ROC4"]
    del df["ROC_MA4"]
    del df["KST_IND"]
    del df["KST"]

    return df

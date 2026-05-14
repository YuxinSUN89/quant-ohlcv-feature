def signal(df, n, factor_name, config):
    eps = config.eps
    # ADTM indicator
    """
    N=20
    DTM=IF(OPEN>REF(OPEN,1),MAX(HIGH-OPEN,OPEN-REF(OP
    EN,1)),0)
    DBM=IF(OPEN<REF(OPEN,1),MAX(OPEN-LOW,REF(OPEN,1)-O
    PEN),0)
    STM=SUM(DTM,N)
    SBM=SUM(DBM,N)
    ADTM=(STM-SBM)/MAX(STM,SBM)
    ADTM measures market sentiment by comparing how much the open price rises vs. falls.
    ADTM values range from -1 to 1. When ADTM crosses above 0.5, market sentiment is strong;
    when ADTM crosses below -0.5, market sentiment is weak. We generate trading signals accordingly.
    A buy signal is generated when ADTM crosses above 0.5;
    a sell signal is generated when ADTM crosses below -0.5.

    """
    df["h_o"] = df["high"] - df["open"]
    df["diff_open"] = df["open"] - df["open"].shift(1)
    max_value1 = df[["h_o", "diff_open"]].max(axis=1)
    df.loc[df["open"] > df["open"].shift(1), "DTM"] = max_value1
    df["DTM"] = df["DTM"].fillna(0)

    df["o_l"] = df["open"] - df["low"]
    max_value2 = df[["o_l", "diff_open"]].max(axis=1)
    # DBM = pd.where(df['open'] < df['open'].shift(1), max_value2, 0)
    df.loc[df["open"] < df["open"].shift(1), "DBM"] = max_value2
    df["DBM"] = df["DBM"].fillna(0)

    df["STM"] = df["DTM"].rolling(n, min_periods=config.min_periods).sum()
    df["SBM"] = df["DBM"].rolling(n, min_periods=config.min_periods).sum()
    max_value3 = df[["STM", "SBM"]].max(axis=1)
    df[factor_name] = (df["STM"] - df["SBM"]) / (max_value3 + eps)

    del df["h_o"]
    del df["diff_open"]
    del df["o_l"]
    del df["STM"]
    del df["SBM"]
    del df["DBM"]
    del df["DTM"]

    return df

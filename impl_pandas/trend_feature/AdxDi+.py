import numpy as np


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
    df["max_high"] = np.where(df["high"] > df["high"].shift(1), df["high"] - df["high"].shift(1), 0)
    # MAX_LOW=IF(REF(LOW,1)>LOW,REF(LOW,1)-LOW,0)
    df["max_low"] = np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)
    # XPDM=IF(MAX_HIGH>MAX_LOW,HIGH-REF(HIGH,1),0)
    df["XPDM"] = np.where(df["max_high"] > df["max_low"], df["high"] - df["high"].shift(1), 0)
    # PDM=SUM(XPDM,N1)
    df["PDM"] = df["XPDM"].rolling(n, min_periods=config.min_periods).sum()
    # XNDM=IF(MAX_LOW>MAX_HIGH,REF(LOW,1)-LOW,0)
    df["XNDM"] = np.where(df["max_low"] > df["max_high"], df["low"].shift(1) - df["low"], 0)
    # NDM=SUM(XNDM,N1)
    df["NDM"] = df["XNDM"].rolling(n, min_periods=config.min_periods).sum()
    # ABS(HIGH-LOW)
    df["c1"] = abs(df["high"] - df["low"])
    # ABS(HIGH-CLOSE)
    df["c2"] = abs(df["high"] - df["close"])
    # ABS(LOW-CLOSE)
    df["c3"] = abs(df["low"] - df["close"])
    # TR=MAX([ABS(HIGH-LOW),ABS(HIGH-CLOSE),ABS(LOW-CLOSE)])
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)
    # TR=SUM(TR,N1)
    df["TR_sum"] = df["TR"].rolling(n, min_periods=config.min_periods).sum()
    # DI+=PDM/TR
    df[factor_name] = df["PDM"] / df["TR"]  # DI+
    # DI-=NDM/TR
    # df['DI-'] = df['NDM'] / df['TR'] #DI-

    # df[f'ADX_DI+_bh_{n}'] = df['DI+'].shift(1)
    # df[f'ADX_DI-_bh_{n}'] = df['DI-'].shift(1)
    # normalize
    # df[factor_name] = (df['PDM'] + df['NDM']) / df['TR']

    # remove intermediate data
    del df["max_high"]
    del df["max_low"]
    del df["XPDM"]
    del df["PDM"]
    del df["XNDM"]
    del df["NDM"]
    del df["c1"]
    del df["c2"]
    del df["c3"]
    del df["TR"]
    del df["TR_sum"]

    return df

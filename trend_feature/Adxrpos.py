import numpy as np
import pandas as pd


def signal(df, n, factor_name, config):
    # Adx indicator
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
    Di+=PDM/TR
    Di-=NDM/TR
    The Di+ and Di- indicators in the Adx calculation use the differences in consecutive
    daily highs and lows to reflect price trend direction. A buy signal is generated when
    Di+ crosses above Di-; a sell signal when Di+ crosses below Di-.
    """
    max_high = np.where(df["high"] > df["high"].shift(1), df["high"] - df["high"].shift(1), 0)
    max_low = np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)
    xpdm = np.where(pd.Series(max_high) > pd.Series(max_low), pd.Series(max_high) - pd.Series(max_high).shift(1), 0)
    # xndm = np.where(pd.Series(max_low) > pd.Series(max_high), pd.Series(max_low).shift(1) - pd.Series(max_low), 0)
    tr = np.max(
        np.array([(df["high"] - df["low"]).abs(), (df["high"] - df["close"]).abs(), (df["low"] - df["close"]).abs()]),
        axis=0,
    )  # take the maximum of the three series
    pdm = pd.Series(xpdm).rolling(n, min_periods=config.min_periods).sum()
    # ndm = pd.Series(xndm).rolling(n, min_periods=config.min_periods).sum()

    di_pos = pd.Series(pdm / pd.Series(tr).rolling(n, min_periods=config.min_periods).sum())
    # di_neg = pd.Series(ndm / pd.Series(tr).rolling(n, min_periods=config.min_periods).sum())

    df[factor_name] = 0.5 * pd.Series(di_pos) + 0.5 * pd.Series(di_pos).shift(n)

    return df

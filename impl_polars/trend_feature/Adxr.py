import numpy as np
import polars as pl


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
    max_high = pl.Series(max_high).fill_nan(None)
    max_low = np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)
    max_low = pl.Series(max_low).fill_nan(None)
    # tol=config.normalize_eps: guard against CSV float-parsing ULP differences causing boundary condition flips
    tol = config.normalize_eps
    xpdm = np.where(max_high > max_low + tol, pl.Series(max_high).fill_nan(None) - pl.Series(max_high).shift(1), 0)
    xndm = np.where(max_low > max_high + tol, pl.Series(max_low).fill_nan(None).shift(1) - pl.Series(max_low), 0)
    tr = np.max(
        np.array([(df["high"] - df["low"]).abs(), (df["high"] - df["close"]).abs(), (df["low"] - df["close"]).abs()]),
        axis=0,
    )  # take the maximum of the three series
    pdm = pl.Series(xpdm).rolling_sum(n, min_samples=config.min_periods)
    ndm = pl.Series(xndm).rolling_sum(n, min_samples=config.min_periods)

    di_pos = pl.Series(pdm / pl.Series(tr).rolling_sum(n, min_samples=config.min_periods))
    di_neg = pl.Series(ndm / pl.Series(tr).rolling_sum(n, min_samples=config.min_periods))

    adxr_pos = 0.5 * pl.Series(di_pos) + 0.5 * pl.Series(di_pos).shift(n)
    adxr_neg = 0.5 * pl.Series(di_neg) + 0.5 * pl.Series(di_neg).shift(n)

    df = df.with_columns(pl.Series(factor_name, adxr_pos - adxr_neg))

    return df

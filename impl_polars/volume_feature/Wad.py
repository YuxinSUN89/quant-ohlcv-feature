import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    eps = config.eps
    #  WAD indicator
    """
    TRH=MAX(HIGH,REF(CLOSE,1))
    TRL=MIN(LOW,REF(CLOSE,1))
    AD=IF(CLOSE>REF(CLOSE,1),CLOSE-TRL,CLOSE-TRH)
    AD=IF(CLOSE==REF(CLOSE,1),0,AD)
    WAD=CUMSUM(AD)
    N=20
    WADMA=MA(WAD,N)
    Reference: https://zhidao.baidu.com/question/19720557.html
    If today's close > yesterday's close, A/D = close minus the smaller of yesterday's close and today's low;
    If today's close < yesterday's close, A/D = close minus the larger of yesterday's close and today's high;
    If today's close == yesterday's close, A/D = 0;
    WAD = cumulative sum of A/D from the first trading day;
    """
    df = df.with_columns(pl.Series("ref_close", df["close"].shift(1)))
    df = df.with_columns(TRH=pl.max_horizontal([pl.col("high"), pl.col("ref_close")]))
    df = df.with_columns(pl.Series("TRL", df.select(pl.min_horizontal([pl.col("low"), pl.col("ref_close")]))["low"]))
    df = df.with_columns(
        pl.Series(
            "AD", np.where(df["close"] > df["close"].shift(1), df["close"] - df["TRL"], df["close"] - df["TRH"])
        ).fill_nan(None)
    )
    df = df.with_columns(pl.Series("AD", np.where(df["close"] == df["close"].shift(1), 0, df["AD"])).fill_nan(None))
    df = df.with_columns(pl.Series("WAD", df["AD"].cum_sum()))
    df = df.with_columns(pl.Series("WADMA", df["WAD"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["WAD"] / (df["WADMA"] + eps)))

    df = df.drop("ref_close")
    df = df.drop(["TRH", "TRL"])
    df = df.drop("AD")
    df = df.drop("WAD")
    df = df.drop("WADMA")

    return df

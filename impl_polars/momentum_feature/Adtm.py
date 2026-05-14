import polars as pl


def signal(df, n, factor_name, config):
    # ADTM indicator
    """
    N=20
    DTM=IF(OPEN>REF(OPEN,1),MAX(HIGH-OPEN,OPEN-REF(OPEN,1)),0)
    DBM=IF(OPEN<REF(OPEN,1),MAX(OPEN-LOW,REF(OPEN,1)-OPEN),0)
    STM=SUM(DTM,N)
    SBM=SUM(DBM,N)
    ADTM=(STM-SBM)/MAX(STM,SBM)
    ADTM measures market sentiment by comparing how much the open price rises vs. falls.
    ADTM values range from -1 to 1. When ADTM crosses above 0.5, market sentiment is strong;
    when ADTM crosses below -0.5, market sentiment is weak. We generate trading signals accordingly.
    A buy signal is generated when ADTM crosses above 0.5;
    a sell signal is generated when ADTM crosses below -0.5.
    """
    df = df.with_columns(
        h_o=pl.col("high") - pl.col("open"),
        diff_open=pl.col("open") - pl.col("open").shift(1),
    )
    df = df.with_columns(
        DTM=pl.when(pl.col("open") > pl.col("open").shift(1))
        .then(pl.max_horizontal([pl.col("h_o"), pl.col("diff_open")]))
        .otherwise(0.0)
    )

    df = df.with_columns(
        o_l=pl.col("open") - pl.col("low"),
    )
    df = df.with_columns(
        DBM=pl.when(pl.col("open") < pl.col("open").shift(1))
        .then(pl.max_horizontal([pl.col("o_l"), pl.col("diff_open")]))
        .otherwise(0.0)
    )

    df = df.with_columns(
        STM=pl.col("DTM").rolling_sum(n, min_samples=config.min_periods),
        SBM=pl.col("DBM").rolling_sum(n, min_samples=config.min_periods),
    )
    df = df.with_columns(max_val=pl.max_horizontal([pl.col("STM"), pl.col("SBM")]))
    df = df.with_columns(pl.Series(factor_name, (df["STM"] - df["SBM"]) / (df["max_val"] + config.eps)))

    df = df.drop(["h_o", "diff_open", "o_l", "STM", "SBM", "DBM", "DTM", "max_val"])

    return df

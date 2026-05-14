import polars as pl


def signal(df, n, factor_name, config):
    # VI indicator
    """
    TR=MAX([ABS(HIGH-LOW),ABS(LOW-REF(CLOSE,1)),ABS(HIG
    H-REF(CLOSE,1))])
    VMPOS=ABS(HIGH-REF(LOW,1))
    VMNEG=ABS(LOW-REF(HIGH,1))
    N=40
    SUMPOS=SUM(VMPOS,N)
    SUMNEG=SUM(VMNEG,N)
    TRSUM=SUM(TR,N)
    VI+=SUMPOS/TRSUM
    VI-=SUMNEG/TRSUM
    VI can be seen as a variant of ADX. VI+ and VI- in the VI indicator are similar to
    DI+ and DI- in ADX. The difference is that ADX uses the differences between current and
    previous high prices and between current and previous low prices to measure price change,
    while VI uses the differences between current high and previous low, and current low and
    previous high. When VI+ crosses above/below VI-, the bull/bear signal strengthens, generating buy/sell signals.
    """
    df = df.with_columns(pl.Series("c1", abs(df["high"] - df["low"])))
    df = df.with_columns(pl.Series("c2", abs(df["close"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))

    df = df.with_columns(pl.Series("VMPOS", abs(df["high"] - df["low"].shift(1))))
    df = df.with_columns(pl.Series("VMNEG", abs(df["low"] - df["high"].shift(1))))
    df = df.with_columns(pl.Series("sum_pos", df["VMPOS"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("sum_neg", df["VMNEG"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series("sum_tr", df["TR"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["sum_pos"] / df["sum_tr"]))  # Vi+
    # df['VI-'] = df['sum_neg'] / df['sum_tr'] #Vi-

    df = df.drop("c1")
    df = df.drop("c2")
    df = df.drop("c3")
    df = df.drop("TR")
    df = df.drop("VMPOS")
    df = df.drop("VMNEG")
    df = df.drop("sum_pos")
    df = df.drop("sum_neg")
    df = df.drop("sum_tr")

    return df

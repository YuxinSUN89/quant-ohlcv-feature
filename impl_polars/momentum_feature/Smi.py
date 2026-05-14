import polars as pl


def signal(df, n, factor_name, config):
    # SMI indicator
    """
    N1=20
    N2=20
    N3=20
    M=(MAX(HIGH,N1)+MIN(LOW,N1))/2
    D=CLOSE-M
    DS=EMA(EMA(D,N2),N2)
    DHL=EMA(EMA(MAX(HIGH,N1)-MIN(LOW,N1),N2),N2)
    SMI=100*DS/DHL
    SMIMA=MA(SMI,N3)
    SMI can be seen as a variant of KDJ. The difference is that KD measures where today's
    closing price falls between the highest and lowest prices over the past N days, while SMI
    measures the distance between today's closing price and the midpoint of those extremes.
    Buy/sell signals are generated when SMI crosses above/below its moving average.
    """
    df = df.with_columns(pl.Series("max_high", df["high"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("min_low", df["low"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("M", (df["max_high"] + df["min_low"]) / 2))
    df = df.with_columns(pl.Series("D", df["close"] - df["M"]))
    df = df.with_columns(pl.Series("ema", df["D"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("DS", df["ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("HL", df["max_high"] - df["min_low"]))
    df = df.with_columns(pl.Series("ema_hl", df["HL"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("DHL", df["ema_hl"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("SMI", 100 * df["DS"] / df["DHL"]))
    df = df.with_columns(pl.Series(factor_name, df["SMI"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop("max_high")
    df = df.drop("min_low")
    df = df.drop("M")
    df = df.drop("D")
    df = df.drop("ema")
    df = df.drop("DS")
    df = df.drop("HL")
    df = df.drop("ema_hl")
    df = df.drop("DHL")
    df = df.drop("SMI")

    return df

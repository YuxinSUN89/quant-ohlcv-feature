from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** smi ********************
    # --- SMI --- 073/125
    # N1=20
    # N2=20
    # N3=20
    # M=(Smi_v2X(HIGH,N1)+MIN(LOW,N1))/2
    # D=CLOSE-M
    # DS=ESmi_v2(ESmi_v2(D,N2),N2)
    # DHL=ESmi_v2(ESmi_v2(Smi_v2X(HIGH,N1)-MIN(LOW,N1),N2),N2)
    # SMI=100*DS/DHL
    # SMISmi_v2=Smi_v2(SMI,N3)
    # SMI can be seen as a variant of KDJ. The difference is that KD measures where today's
    # closing price falls between the highest and lowest prices over the past N days, while SMI
    # measures the distance between today's closing price and the midpoint of those extremes.
    # Buy/sell signals are generated when SMI crosses above/below its moving average.

    m = (
        0.5 * df["high"].rolling(n, min_periods=config.min_periods).max()
        + 0.5 * df["low"].rolling(n, min_periods=config.min_periods).min()
    )
    d = df["close"] - m
    ds = d.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    ds = ds.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()

    dhl = (
        df["high"].rolling(n, min_periods=config.min_periods).max()
        - df["low"].rolling(n, min_periods=config.min_periods).min()
    )
    dhl = dhl.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    dhl = dhl.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()

    smi = 100 * ds / dhl

    s = smi.rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df

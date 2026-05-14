import polars as pl

from impl_polars.helpers import scale_01


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

    m = 0.5 * df["high"].rolling_max(n, min_samples=config.min_periods) + 0.5 * df["low"].rolling_min(
        n, min_samples=config.min_periods
    )
    d = df["close"] - m
    ds = d.ewm_mean(span=n, adjust=config.ewm_adjust)
    ds = ds.ewm_mean(span=n, adjust=config.ewm_adjust)

    dhl = df["high"].rolling_max(n, min_samples=config.min_periods) - df["low"].rolling_min(
        n, min_samples=config.min_periods
    )
    dhl = dhl.ewm_mean(span=n, adjust=config.ewm_adjust)
    dhl = dhl.ewm_mean(span=n, adjust=config.ewm_adjust)

    smi = 100 * ds / dhl

    s = smi.rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

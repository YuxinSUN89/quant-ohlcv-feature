import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** Pac ********************
    # N1=20
    # N2=20
    # UPPER=SMA(HIGH,N1,1)
    # LOWER=SMA(LOW,N2,1)
    # Construct a price channel using moving averages of high and low prices. Go long if price breaks above the upper band; go short if it breaks below the lower band.
    lower = df["low"].ewm_mean(alpha=1 / n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series(factor_name, scale_01(lower, n, config.normalize_eps, config=config)))

    return df

from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** Pac ********************
    # N1=20
    # N2=20
    # UPPER=SMA(HIGH,N1,1)
    # LOWER=SMA(LOW,N2,1)
    # Construct a price channel using moving averages of high and low prices. Go long if price breaks above the upper band; go short if it breaks below the lower band.
    upper = df["high"].ewm(alpha=1 / n, adjust=config.ewm_adjust).mean()
    upper = df["close"] - upper

    df[factor_name] = scale_01(upper, n, config.normalize_eps, config=config)

    return df

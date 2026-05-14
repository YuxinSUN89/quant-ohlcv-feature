import polars as pl


def signal(df, n, factor_name, config):
    # ADOSC indicator
    """
    AD=CUM_SUM(((CLOSE-LOW)-(HIGH-CLOSE))*VOLUME/(HIGH-LOW))
    AD_EMA1=EMA(AD,N1)
    AD_EMA2=EMA(AD,N2)
    ADOSC=AD_EMA1-AD_EMA2
    The ADL (Accumulation/Distribution Line) indicator is the weighted cumulative sum of
    trading volume, where the weight is the CLV indicator. ADL is analogous to OBV, but
    while OBV splits volume into positive/negative based on price direction, ADL uses CLV
    as a weight for cumulating volume. CLV measures where the close is between the low and
    high: CLV>0(<0) means the close is closer to the high (low). When CLV is closer to 1(-1),
    the close is closer to the high (low). If CLV>0 on a given day, ADL adds volume*CLV
    (accumulation); if CLV<0, ADL subtracts volume*CLV (distribution).
    ADOSC is the difference between the short-term and long-term moving averages of ADL.
    A buy signal is generated when ADOSC crosses above 0; a sell signal when it crosses below 0.
    """
    df = df.with_columns(
        pl.Series(
            "AD", ((df["close"] - df["low"]) - (df["high"] - df["close"])) * df["volume"] / (df["high"] - df["low"])
        )
    )
    df = df.with_columns(pl.Series("AD_sum", df["AD"].cum_sum()))
    df = df.with_columns(pl.Series("AD_EMA1", df["AD_sum"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("AD_EMA2", df["AD_sum"].ewm_mean(span=n * 2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ADOSC", df["AD_EMA1"] - df["AD_EMA2"]))

    # normalize
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["ADOSC"] - df["ADOSC"].rolling_min(n, min_samples=config.min_periods))
            / (
                df["ADOSC"].rolling_max(n, min_samples=config.min_periods)
                - df["ADOSC"].rolling_min(n, min_samples=config.min_periods)
            ),
        )
    )

    df = df.drop("AD")
    df = df.drop("AD_sum")
    df = df.drop("AD_EMA2")
    df = df.drop("AD_EMA1")
    df = df.drop("ADOSC")

    return df

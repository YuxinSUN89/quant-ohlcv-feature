import talib as ta


def signal(df, n, factor_name, config):
    # VolumeTSF indicator (Time Series Forecast of Quote Volume)
    # Formula: result = TSF(QUOTE_VOLUME, N)
    # Applies talib's Time Series Forecast (linear regression extrapolation) to quote volume.
    # Projects the volume trend one step ahead based on the linear regression over N periods.
    # Useful for estimating whether volume is trending up or down relative to recent history.
    df[factor_name] = ta.TSF(df["quote_volume"], timeperiod=n)

    return df

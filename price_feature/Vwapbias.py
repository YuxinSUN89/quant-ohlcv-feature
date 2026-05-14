def signal(df, n, factor_name, config):
    # Vwapbias indicator
    """
    Replace the close price in bias with vwap.

    VWAP=quote_volume/volume (volume-weighted average price within the period)
    MA=moving average of VWAP
    factor = VWAP / MA - 1 (normalize)

    """
    eps = config.eps
    df["vwap"] = df["quote_volume"] / df["volume"]  # quote_volume / volume = volume-weighted average price
    ma = df["vwap"].rolling(n, min_periods=config.min_periods).mean()  # compute moving average
    df[factor_name] = df["vwap"] / (ma + eps) - 1  # normalize

    del df["vwap"]

    return df

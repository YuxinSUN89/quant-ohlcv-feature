def signal(df, n, factor_name, config):
    # WVAD indicator
    """
    N=20
    WVAD=SUM(((CLOSE-OPEN)/(HIGH-LOW)*VOLUME),N)
    WVAD is a price-volume indicator that weights trading volume by price information,
    used to compare the strength of buyers and sellers from open to close.
    WVAD is similar in construction to CMF, but CMF uses CLV (reflecting where the close
    is between high and low) as the weight, while WVAD uses the distance between close
    and open (i.e., the length of the candle body) as a proportion of the high-low range,
    and does not divide by the sum of volume.
    When WVAD crosses above 0, it indicates strong buying power;
    when WVAD crosses below 0, it indicates strong selling power.
    """
    df["VAD"] = (df["close"] - df["open"]) / (df["high"] - df["low"]) * df["volume"]
    df["WVAD"] = df["VAD"].rolling(n, min_periods=config.min_periods).sum()

    # normalize
    df[factor_name] = (df["WVAD"] - df["WVAD"].rolling(n, min_periods=config.min_periods).min()) / (
        df["WVAD"].rolling(n, min_periods=config.min_periods).max()
        - df["WVAD"].rolling(n, min_periods=config.min_periods).min()
    )

    del df["VAD"]
    del df["WVAD"]

    return df

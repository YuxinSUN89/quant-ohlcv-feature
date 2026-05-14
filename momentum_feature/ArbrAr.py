def signal(df, n, factor_name, config):
    # ARBR indicator
    """
    AR=SUM((HIGH-OPEN),N)/SUM((OPEN-LOW),N)*100
    # BR=SUM((HIGH-REF(CLOSE,1)),N)/SUM((REF(CLOSE,1)-LOW),N)*100
    AR measures where the open price falls between the high and low; BR measures where
    yesterday's close falls between today's high and low. AR is a sentiment indicator
    measuring the balance between bulls and bears. When AR is low (below 50), sentiment is
    very weak; if AR crosses above 50 from below, prices may rise — buy at the low.
    Sell when AR crosses below 200.
    """
    df["HO"] = df["high"] - df["open"]
    df["OL"] = df["open"] - df["low"]
    df[factor_name] = (
        df["HO"].rolling(n, min_periods=config.min_periods).sum()
        / df["OL"].rolling(n, min_periods=config.min_periods).sum()
        * 100
    )

    del df["HO"]
    del df["OL"]

    return df

import polars as pl


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
    df = df.with_columns(pl.Series("HO", df["high"] - df["open"]))
    df = df.with_columns(pl.Series("OL", df["open"] - df["low"]))
    df = df.with_columns(
        pl.Series(
            factor_name,
            df["HO"].rolling_sum(n, min_samples=config.min_periods)
            / df["OL"].rolling_sum(n, min_samples=config.min_periods)
            * 100,
        )
    )

    df = df.drop("HO")
    df = df.drop("OL")

    return df

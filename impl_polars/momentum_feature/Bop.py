import polars as pl


def signal(df, n, factor_name, config):
    # BOP indicator
    """
    N=20
    BOP=MA((CLOSE-OPEN)/(HIGH-LOW),N)
    BOP ranges from -1 to 1 and measures the ratio of the distance (positive or negative)
    between close and open prices to the distance between high and low prices, reflecting the
    bull/bear power balance in the market.
    If BOP>0, bulls have more advantage; BOP<0 means bears dominate. The larger the BOP,
    the more the price has been pushed toward the high; the smaller the BOP, the more
    the price has been pushed toward the low. We can use BOP crossing above/below 0 to generate buy/sell signals.
    """
    df = df.with_columns(pl.Series("co", df["close"] - df["open"]))
    df = df.with_columns(pl.Series("hl", df["high"] - df["low"]))
    df = df.with_columns(pl.Series(factor_name, (df["co"] / df["hl"]).rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop("co")
    df = df.drop("hl")

    return df

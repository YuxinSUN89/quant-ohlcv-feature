import polars as pl


def signal(df, n, factor_name, config):
    # Clv indicator
    # CLV=(2*CLOSE-LOW-HIGH)/(HIGH-LOW)
    df = df.with_columns(pl.Series("CLV", (2 * df["close"] - df["low"] - df["high"]) / (df["high"] - df["low"])))
    df = df.with_columns(
        pl.Series(factor_name, df["CLV"].rolling_mean(n, min_samples=config.min_periods))
    )  # CLVMA=MA(CLV,N)

    # delete extra columns
    df = df.drop("CLV")

    return df

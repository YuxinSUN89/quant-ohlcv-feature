import polars as pl


def signal(df, n, factor_name, config):
    # How many minutes in the past n minutes showed a price increase
    df = df.with_columns(pl.Series("_ret_sign", df["close"].pct_change().fill_null(0) > 0))
    df = df.with_columns(pl.Series(factor_name, df["_ret_sign"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.drop("_ret_sign")

    return df

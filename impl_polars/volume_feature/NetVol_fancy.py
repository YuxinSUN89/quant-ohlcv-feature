import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Quote volume weighted by the sign of returns, simulating net capital inflow/outflow
    df = df.with_columns(pl.Series("_ret_sign", np.sign(df["close"].pct_change())))
    df = df.with_columns(
        pl.Series(factor_name, (df["_ret_sign"] * df["quote_volume"]).rolling_sum(n, min_samples=config.min_periods))
    )

    df = df.drop("_ret_sign")

    return df

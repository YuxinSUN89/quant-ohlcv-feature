"""
Strategy Sharing Session
Position Management Framework

Copyright reserved.

This code is for personal learning use only. Copying, modification, or commercial use without authorization is prohibited.
"""

import polars as pl


def signal(df, n, factor_name, config):
    df = df.with_columns(pl.Series(factor_name, df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)))

    return df


from impl_polars.helpers import rolling_mean_multi


def signal_multi_params(df, param_list, config) -> dict:
    return rolling_mean_multi(df, param_list, "quote_volume", config)

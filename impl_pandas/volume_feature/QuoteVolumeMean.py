"""
Strategy Sharing Session
Position Management Framework

Copyright reserved.

This code is for personal learning use only. Copying, modification, or commercial use without authorization is prohibited.
"""


def signal(df, n, factor_name, config):
    df[factor_name] = df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()

    return df


from impl_pandas.helpers import rolling_mean_multi


def signal_multi_params(df, param_list, config) -> dict:
    return rolling_mean_multi(df, param_list, "quote_volume", config)

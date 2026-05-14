import numpy as np


def signal(df, n, factor_name, config):
    # Quote volume weighted by the sign of returns, simulating net capital inflow/outflow
    df["_ret_sign"] = np.sign(df["close"].pct_change())
    df[factor_name] = (df["_ret_sign"] * df["quote_volume"]).rolling(n, min_periods=config.min_periods).sum()

    del df["_ret_sign"]

    return df

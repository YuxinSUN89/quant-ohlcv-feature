def signal(df, n, factor_name, config):
    # How many minutes in the past n minutes showed a price increase
    df["_ret_sign"] = df["close"].pct_change() > 0
    df[factor_name] = df["_ret_sign"].rolling(n, min_periods=config.min_periods).sum()

    del df["_ret_sign"]

    return df

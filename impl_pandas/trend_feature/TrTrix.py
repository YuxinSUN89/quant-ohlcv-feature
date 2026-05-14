def signal(df, n, factor_name, config):
    # TrTrix indicator (single EMA percentage change)
    # Formula: EMA1 = EMA(CLOSE,N); result = EMA1.pct_change()
    # Simplified variant of TRIX using only a single EMA layer.
    # Measures the 1-period rate of change of the EMA, capturing short-term trend momentum.
    df["tr_trix"] = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df[factor_name] = df["tr_trix"].pct_change()

    # remove redundant columns
    del df["tr_trix"]

    return df

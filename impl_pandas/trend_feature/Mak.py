def signal(df, n, factor_name, config):
    # Mak indicator (Rate of change of MA × 1000)
    # Formula: MA = MA(CLOSE, N); result = (MA / REF(MA,1) - 1) * 1000
    # Measures how fast the moving average is changing (1-period ROC of MA), amplified by 1000.
    # Positive values indicate MA is rising; negative indicate it's falling.
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = (
        df["ma"] / (df["ma"] + config.eps).shift(1) - 1
    ) * 1000  # Original price change value is too small, multiply by 1000 to amplify.

    del df["ma"]

    return df

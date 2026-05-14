def signal(df, n, factor_name, config):
    # Rbias indicator (Rate of change of Bias)
    # Formula: BIAS = CLOSE / MA(CLOSE, N); result = BIAS / REF(BIAS, 1) - 1
    # Measures the 1-period change in the price-to-MA ratio, i.e., how fast the bias is growing or shrinking.
    # Positive values indicate bias is increasing (price diverging further from MA upward).
    ma = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = (df["close"] / ma) / (df["close"].shift(1) / ma.shift(1)) - 1

    return df

def signal(df, n, factor_name, config):
    # Roc indicator (Simple N-period Rate of Change)
    # Formula: ROC = CLOSE / REF(CLOSE, N) - 1
    # Measures the proportional price change over N periods (similar to Mtm but without ×100).
    # Positive values indicate upward movement; negative indicate downward movement.
    df[factor_name] = df["close"] / (df["close"].shift(n) + config.eps) - 1

    return df

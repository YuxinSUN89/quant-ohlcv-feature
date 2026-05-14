def signal(df, n, factor_name, config):
    # Mtm indicator (Simple N-period momentum)
    # Formula: MTM = (CLOSE / REF(CLOSE, N) - 1) * 100
    # Measures the percentage price change over N periods. Positive values indicate upward momentum.
    # The most basic momentum indicator; useful as a building block for composite factors.
    df[factor_name] = (df["close"] / (df["close"].shift(n) + config.eps) - 1) * 100

    return df

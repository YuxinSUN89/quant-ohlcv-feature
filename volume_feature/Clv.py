def signal(df, n, factor_name, config):
    # Clv indicator
    # CLV=(2*CLOSE-LOW-HIGH)/(HIGH-LOW)
    df["CLV"] = (2 * df["close"] - df["low"] - df["high"]) / (df["high"] - df["low"])
    df[factor_name] = df["CLV"].rolling(n, min_periods=config.min_periods).mean()  # CLVMA=MA(CLV,N)

    # delete extra columns
    del df["CLV"]

    return df

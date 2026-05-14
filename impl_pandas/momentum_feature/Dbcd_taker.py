def signal(df, n, factor_name, config):
    # Dbcd_taker indicator (DBCD Bias × Taker buy ratio)
    # Formula: BIAS = (CLOSE - MA(CLOSE,N)) / MA(CLOSE,N) * 100
    #          BIAS_DIF = BIAS - REF(BIAS, 3N); DBCD = MA(BIAS_DIF, 3N+2)
    #          TAKER_RATIO = SUM(taker_buy,N) / SUM(quote_volume,N)
    #          result = DBCD * TAKER_RATIO
    # Multiplies the DBCD momentum oscillator by the taker buy ratio.
    # Amplifies the buy signal when both momentum and buy-side volume confirm the uptrend.
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["Bias"] = (df["close"] - df["ma"]) / (df["ma"] + config.eps) * 100
    df["Bias_DIF"] = df["Bias"] - df["Bias"].shift(3 * n)

    volume = df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
    buy_volume = df["taker_buy_quote_asset_volume"].rolling(n, min_periods=config.min_periods).sum()

    df[factor_name] = df["Bias_DIF"].rolling(3 * n + 2, min_periods=config.min_periods).mean() * (buy_volume / volume)

    del df["ma"]
    del df["Bias"]
    del df["Bias_DIF"]

    return df

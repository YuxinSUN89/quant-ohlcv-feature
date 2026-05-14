def signal(df, n, factor_name, config):
    # Vao_v2 indicator (Volume Analysis Oscillator v2)
    # Formula: WV = VOLUME * (CLOSE - 0.5*HIGH - 0.5*LOW); VAO = WV + REF(WV, 1)
    #          VAO_MA1 = MA(VAO, N); VAO_MA2 = MA(VAO, 3N)
    #          Vao_v2 = VAO_MA1 - VAO_MA2; signal = VAO / Vao_v2 - 1
    # WV weights volume by how much the close price deviates from the midpoint of high and low.
    # A positive WV (close above midpoint) indicates buying pressure; negative indicates selling pressure.
    # The crossover of short and long VAO MAs generates trend signals.
    df["WV"] = df["volume"] * (df["close"] - 0.5 * df["high"] - 0.5 * df["low"])
    df["VAO"] = df["WV"] + df["WV"].shift(1)
    df["VAO_MA1"] = df["VAO"].rolling(n, min_periods=config.min_periods).mean()
    df["VAO_MA2"] = df["VAO"].rolling(3 * n, min_periods=config.min_periods).mean()
    df["Vao_v2"] = df["VAO_MA1"] - df["VAO_MA2"]

    # normalize
    df[factor_name] = df["VAO"] / df["Vao_v2"] - 1

    return df

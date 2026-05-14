def signal(df, n, factor_name, config):
    # CoppAtrBull indicator (COPP × ATR × taker buy activity composite)
    # Formula: COPP = MA(100*((CLOSE-REF(CLOSE,N))/REF(CLOSE,N) + (CLOSE-REF(CLOSE,2N))/REF(CLOSE,2N)), N)
    #          ATR = MA(TR,N) / MA(CLOSE,N)  (normalized average true range)
    #          TAKER_BUY = MA(TAKER_BUY_QUOTE_VOLUME / MA(QUOTE_VOLUME,N) * 100, N)
    #          result = COPP * ATR * TAKER_BUY
    # Composite of Coppock momentum, volatility (ATR), and bullish taker buy pressure.
    # High positive values indicate momentum up with expanding volatility and strong buy activity.
    # COPP
    # RC=100*((CLOSE-REF(CLOSE,N1))/REF(CLOSE,N1)+(CLOSE-REF(CLOSE,N2))/REF(CLOSE,N2))
    df["RC"] = 100 * (
        (df["close"] - df["close"].shift(n)) / df["close"].shift(n)
        + (df["close"] - df["close"].shift(2 * n)) / df["close"].shift(2 * n)
    )
    df["RC_mean"] = df["RC"].rolling(n, min_periods=config.min_periods).mean()

    # ATR
    df["median"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["c1"] = df["high"] - df["low"]  # HIGH-LOW
    df["c2"] = abs(df["high"] - df["close"].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df["c3"] = abs(df["low"] - df["close"].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)  # TR=MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1)),ABS(LOW-REF(CLOSE,1)))
    df["_ATR"] = df["TR"].rolling(n, min_periods=config.min_periods).mean()  # ATR=MA(TR,N)
    # normalize ATR indicator
    df["ATR"] = df["_ATR"] / df["median"]

    # average taker buy ratio
    df["vma"] = df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    df["taker_buy_ma"] = (df["taker_buy_quote_asset_volume"] / df["vma"]) * 100
    df["taker_buy_mean"] = df["taker_buy_ma"].rolling(window=n, min_periods=config.min_periods).mean()

    # composite indicator
    df[factor_name] = df["RC_mean"] * df["ATR"] * df["taker_buy_mean"]
    # delete extra columns
    del df["RC"], df["RC_mean"]
    del df["median"], df["c1"], df["c2"], df["c3"], df["TR"], df["_ATR"], df["ATR"]
    del df["vma"], df["taker_buy_ma"], df["taker_buy_mean"]

    return df

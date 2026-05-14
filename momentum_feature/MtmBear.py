def signal(df, n, factor_name, config):
    # MtmBear indicator (MTM mean × ATR × Taker sell composite)
    # Formula: MTM_MEAN = MA(CLOSE/REF(MA,N)-1, N) * 100; ATR = MA(TR,N)/MA * 100
    #          TAKER_SELL_MEAN = MA(taker_sell/MA(quote_volume)*100, N)
    #          result = MTM_MEAN * ATR * TAKER_SELL_MEAN
    # Bearish composite: momentum × volatility × seller-initiated volume.
    # Large positive values indicate strong downside momentum in a volatile, seller-dominated market.
    # momentum
    df["ma"] = df["close"].rolling(window=n, min_periods=config.min_periods).mean()
    df["mtm"] = (df["close"] / df["ma"].shift(n) - 1) * 100
    df["mtm_mean"] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean()

    # average amplitude
    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = abs(df["high"] - df["close"].shift(1))
    df["tr3"] = abs(df["low"] - df["close"].shift(1))
    df["tr"] = df[["tr1", "tr2", "tr3"]].max(axis=1)
    df["ATR_abs"] = df["tr"].rolling(window=n, min_periods=config.min_periods).mean()
    df["ATR"] = df["ATR_abs"] / df["ma"] * 100

    # average taker sell volume
    df["taker_sell_quote_asset_volume"] = df["quote_volume"] - df["taker_buy_quote_asset_volume"]
    df["vma"] = df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    df["taker_sell_ma"] = (df["taker_sell_quote_asset_volume"] / df["vma"]) * 100
    df["taker_sell_mean"] = df["taker_sell_ma"].rolling(window=n, min_periods=config.min_periods).mean()

    # combined indicator
    df[factor_name] = df["mtm_mean"] * df["ATR"] * df["taker_sell_mean"]

    drop_col = [
        "ma",
        "mtm",
        "mtm_mean",
        "tr1",
        "tr2",
        "tr3",
        "tr",
        "ATR_abs",
        "ATR",
        "taker_sell_quote_asset_volume",
        "vma",
        "taker_sell_ma",
        "taker_sell_mean",
    ]
    df.drop(columns=drop_col, inplace=True)

    return df

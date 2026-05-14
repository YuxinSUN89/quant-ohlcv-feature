def signal(df, n, factor_name, config):
    # MarketPl_v2 indicator
    eps = config.eps
    # MarketPl_v2 indicator (Market Placement with VWAP-validity check)
    # Formula: AVG_P = QUOTE_VOLUME / VOLUME (if quote_volume > 0, else REF(CLOSE,1))
    #          AVG_COST = EMA(QUOTE_VOLUME,N)/EMA(VOLUME,N) if LOW <= AVG_P <= HIGH, else EMA((O+L+C)/3,N)
    #          result = CLOSE / AVG_COST - 1
    # An enhanced version of MarketPl that validates the VWAP price against the candle range.
    # If VWAP falls outside [LOW, HIGH], it falls back to an EMA of typical price (O+L+C)/3.
    # Measures how far current price is above the estimated average holding cost.
    quote_volume_ema = df["quote_volume"].ewm(span=n, adjust=config.ewm_adjust).mean()
    volume_ema = df["volume"].ewm(span=n, adjust=config.ewm_adjust).mean()
    cost = (df["open"] + df["low"] + df["close"]) / 3
    cost_ema = cost.ewm(span=n, adjust=config.ewm_adjust).mean()
    condition = df["quote_volume"] > 0
    df.loc[condition, "avg_p"] = df["quote_volume"] / df["volume"]
    condition = df["quote_volume"] == 0
    df.loc[condition, "avg_p"] = df["close"].shift(1)
    # Use a tiny tolerance (config.normalize_eps) to absorb CSV float-parsing ULP differences when
    # avg_p (= qv/vol) lands exactly on the candle boundary (close == high/low).
    tol = config.normalize_eps
    condition1 = df["avg_p"] <= df["high"] + tol
    condition2 = df["avg_p"] >= df["low"] - tol
    df.loc[condition1 & condition2, "avg_holding_cost"] = quote_volume_ema / volume_ema
    # Fallback for VWAP outside candle range → use cost_ema
    condition_out = (df["avg_p"] > df["high"] + tol) | (df["avg_p"] < df["low"] - tol)
    df.loc[condition_out, "avg_holding_cost"] = cost_ema
    df[factor_name] = df["close"] / (df["avg_holding_cost"] + eps) - 1

    del df["avg_holding_cost"]

    return df

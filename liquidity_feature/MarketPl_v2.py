eps = 1e-8


def signal(*args):
    # MarketPl_v2 indicator
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # MarketPl_v2 indicator (Market Placement with VWAP-validity check)
    # Formula: AVG_P = QUOTE_VOLUME / VOLUME (if quote_volume > 0, else REF(CLOSE,1))
    #          AVG_COST = EMA(QUOTE_VOLUME,N)/EMA(VOLUME,N) if LOW <= AVG_P <= HIGH, else EMA((O+L+C)/3,N)
    #          result = CLOSE / AVG_COST - 1
    # An enhanced version of MarketPl that validates the VWAP price against the candle range.
    # If VWAP falls outside [LOW, HIGH], it falls back to an EMA of typical price (O+L+C)/3.
    # Measures how far current price is above the estimated average holding cost.
    quote_volume_ema = df['quote_volume'].ewm(span=n, adjust=False).mean()
    volume_ema = df['volume'].ewm(span=n, adjust=False).mean()
    cost = (df['open'] + df['low'] + df['close']) / 3
    cost_ema = cost.ewm(span=n, adjust=False).mean()
    condition = df['quote_volume'] > 0
    df.loc[condition, 'avg_p'] = df['quote_volume'] / df['volume']
    condition = df['quote_volume'] == 0
    df.loc[condition, 'avg_p'] = df['close'].shift(1)
    condition1 = df['avg_p'] <= df['high']
    condition2 = df['avg_p'] >= df['low']
    df.loc[condition1 & condition2, 'avg_holding_cost'] = quote_volume_ema / volume_ema
    condition1 = df['avg_p'] > df['high']
    condition2 = df['avg_p'] < df['low']
    df.loc[condition1 | condition2, 'avg_holding_cost'] = cost_ema
    df[factor_name] = df['close'] / (df['avg_holding_cost'] + eps) - 1

    del df['avg_p']
    del df['avg_holding_cost']

    return df

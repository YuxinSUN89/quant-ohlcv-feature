def signal(*args):

    df = args[0]
    n = args[1]
    factor_name = args[2]

    # Msbt indicator (Momentum × Std-Momentum × BBW × Taker Buy composite)
    # Formula: MTM = MA(CLOSE/REF(CLOSE,N)-1, N); S_MTM = MA(STD/REF(STD,N)-1, N)
    #          BBW = STD(CLOSE,N) / MA(CLOSE,N); TAKER_VOL = SUM(taker_buy,N) / SUM(taker_buy, 0.5N)
    #          MSBT = MTM * S_MTM * BBW_MEAN * TAKER_VOL
    # Combines price momentum, volatility momentum (std change), Bollinger bandwidth, and taker buy activity.
    # High values indicate accelerating price with expanding volatility and strong buying pressure.
    df['ma'] = df['close'].rolling(window=n).mean()
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)

    # close price momentum
    df['mtm'] = df['close'] / df['close'].shift(n) - 1
    df['mtm'] = df['mtm'].rolling(n, min_periods=1).mean()

    # standard deviation momentum
    df['s_mtm'] = df['std'] / df['std'].shift(n) - 1
    df['s_mtm'] = df['s_mtm'].rolling(n, min_periods=1).mean()

    # bbw volatility
    df['bbw'] = df['std'] / df['ma']
    df['bbw_mean'] = df['bbw'].rolling(window=n).mean()
  
    # taker_buy_quote_asset_volume volatility
    df['volatility'] = df['taker_buy_quote_asset_volume'].rolling(window=n, min_periods=1).sum() / \
                   df['taker_buy_quote_asset_volume'].rolling(window=int(0.5 * n), min_periods=1).sum()

    df[factor_name] = df['mtm'] * df['s_mtm'] * df['bbw_mean'] * df['volatility']

    del df['ma']
    del df['std']
    del df['mtm']
    del df['s_mtm']
    del df['bbw']
    del df['bbw_mean']
    del df['volatility']

    return df

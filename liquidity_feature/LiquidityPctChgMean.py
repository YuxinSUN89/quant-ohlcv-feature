eps = 1e-8


def signal(*args):
    # LiquidityPctChgMean indicator (quote volume per unit of price change, averaged)
    # Formula: PCT_CHG_LIQUIDITY = QUOTE_VOLUME / PCT_CHG; result = MA(PCT_CHG_LIQUIDITY, n)
    # Rolling mean of quote volume divided by the day's percentage price change.
    # Higher values mean it has taken more trading value to move price by a given amount — i.e. deeper, more liquid conditions.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)

    df['pct_chg_liq'] = df['quote_volume'] / (df['close'].pct_change() + eps)
    df[factor_name] = df['pct_chg_liq'].rolling(n).mean()
    df.drop(columns=['pct_chg_liq'], errors='ignore', inplace=True)

    return df

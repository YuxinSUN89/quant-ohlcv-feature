eps = 1e-8


def signal(*args):
    # LiquidityPctChgStd indicator (quote volume per unit of price change, dispersion)
    # Formula: PCT_CHG_LIQUIDITY = QUOTE_VOLUME / PCT_CHG; result = STD(PCT_CHG_LIQUIDITY, n)
    # Rolling std of quote volume divided by the day's percentage price change.
    # Higher values mean the amount of volume needed to move price by a given amount has been unusually inconsistent — i.e. unstable liquidity.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)

    df['pct_chg_liq'] = df['quote_volume'] / (df['close'].pct_change() + eps)
    df[factor_name] = df['pct_chg_liq'].rolling(n).std()
    df.drop(columns=['pct_chg_liq'], errors='ignore', inplace=True)

    return df

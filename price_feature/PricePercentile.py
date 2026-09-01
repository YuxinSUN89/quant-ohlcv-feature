def signal(*args):
    # PricePercentile indicator (rolling percentile rank of price)
    # Formula: PricePercentile = rolling percentile rank of CLOSE over n
    # Where the current close ranks, as a percentile, among the last n closes.
    # Near 1 means price is at (or near) its highest point in the window; near 0 means its lowest.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'pricepercentile_0'] = df['close'].rolling(n).rank(pct=True)
    df[factor_name] = df[f'pricepercentile_0']
    df.drop(columns=[f'pricepercentile_0'], errors='ignore', inplace=True)

    return df

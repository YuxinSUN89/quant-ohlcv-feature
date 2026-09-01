def signal(*args):
    # JS indicator (n-day return scaled by lookback length)
    # Formula: JS = 100 * (CLOSE - PREV_CLOSE) / (n * CLOSE.shift(n))
    # The n-day price change normalized by both n and the price n periods ago.
    # A liquidity/return-premium style measure — larger values indicate a stronger return achieved per unit of lookback time.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'JS{n}'] = 100 * (df['close'] - df['close'].shift(n)) / (n * df['close'].shift(n))
    df[factor_name] = df[f'JS{n}']
    df.drop(columns=[f'JS{n}'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # PriceStdN indicator (dispersion of the n-period return ratio)
    # Formula: PriceStdN = STD(CLOSE / CLOSE.shift(n-1), n)
    # Rolling std of close divided by its value n-1 periods ago, over an n-period window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    normalized_price = df['close'] / df['close'].shift(n - 1)
    df[f'Price_Vol_{n}'] = normalized_price.rolling(n).std()
    df[factor_name] = df[f'Price_Vol_{n}']
    df.drop(columns=[f'Price_Vol_{n}'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # PriceVol indicator (n-day price volatility)
    # Formula: PriceVol = STD(n)
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'PriceVol_{n}'] = df['close'].rolling(n).std()
    df[factor_name] = df[f'PriceVol_{n}']
    df.drop(columns=[f'PriceVol_{n}'], errors='ignore', inplace=True)

    return df

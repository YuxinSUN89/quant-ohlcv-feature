def signal(*args):
    # MaHigh indicator (moving average of the session high)
    # Formula: MaHigh = MA(HIGH, n)
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'MaHigh_{n}'] = df['high'].rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'MaHigh_{n}']
    df.drop(columns=[f'MaHigh_{n}'], errors='ignore', inplace=True)

    return df

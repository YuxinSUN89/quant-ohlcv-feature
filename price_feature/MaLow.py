def signal(*args):
    # MaLow indicator (moving average of the session low)
    # Formula: MaLow = MA(LOW, n)
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'MaLow_{n}'] = df['low'].rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'MaLow_{n}']
    df.drop(columns=[f'MaLow_{n}'], errors='ignore', inplace=True)

    return df

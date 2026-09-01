def signal(*args):
    # GapStdN indicator (overnight gap volatility)
    # Formula: GapStdN = STD(abs(PREV_CLOSE / OPEN - 1), n)
    # Rolling std of the absolute overnight gap (prior close vs. today's open) over n days.
    # Higher values indicate the market has been opening away from the prior close by inconsistent amounts.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['prev_close'] = df['close'].shift(1)
    n = int(n)
    df[f'TK_{n}'] = abs(df['prev_close'] / df['open'] - 1)
    df[factor_name] = df[f'TK_{n}'].rolling(n).std()
    df.drop(columns=[f'TK_{n}', 'prev_close'], errors='ignore', inplace=True)

    return df

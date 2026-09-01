def signal(*args):
    # G126 indicator (typical price)
    # Formula: G126 = (CLOSE+HIGH+LOW)/3
    # Simple average of close, high and low for the bar.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G126'] = (df['close'] + df['high'] + df['low']) / 3
    df[factor_name] = df['G126']
    df.drop(columns=['G126'], errors='ignore', inplace=True)

    return df

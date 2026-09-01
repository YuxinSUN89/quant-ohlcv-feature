def signal(*args):
    # H6 indicator (negative open/traded-value correlation)
    # Formula: H6 = -1 * correlation(OPEN, AMOUNT, 10)
    # Negative of the 10-day rolling correlation between the opening price and traded value (compare to G139's volume version).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H6'] = -1 * df['open'].rolling(10, min_periods=1).corr(df['quote_volume'])
    df[factor_name] = df['H6']
    df.drop(columns=['H6'], errors='ignore', inplace=True)

    return df

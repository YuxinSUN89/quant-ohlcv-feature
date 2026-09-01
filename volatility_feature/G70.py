def signal(*args):
    # G70 indicator (6-day std of traded value)
    # Formula: G70 = STD(AMOUNT,6)
    # Rolling 6-day standard deviation of trading value (amount).
    # Higher values indicate turnover has been unusually erratic recently.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G70'] = df['quote_volume'].rolling(6).std()
    df[factor_name] = df['G70']
    df.drop(columns=['G70'], errors='ignore', inplace=True)

    return df

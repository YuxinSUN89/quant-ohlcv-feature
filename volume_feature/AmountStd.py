def signal(*args):
    # AmountStd indicator (dispersion of traded value)
    # Formula: AmountStd = n-day rolling std of QUOTE_VOLUME
    # Rolling n-day standard deviation of quote volume.
    # Higher values mean trading value has been unusually erratic recently.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[factor_name] = df['quote_volume'].rolling(n).std()

    return df

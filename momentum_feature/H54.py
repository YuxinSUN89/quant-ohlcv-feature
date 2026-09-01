def signal(*args):
    # H54 indicator (power-weighted low/close vs. open ratio)
    # Formula: H54 = ((-1 * ((LOW -CLOSE) * (OPEN^5))) / ((LOW -HIGH) * (CLOSE^5)))
    # A ratio of (low-close)*open^5 to (low-high)*close^5, emphasizing the open and close via a 5th-power weighting.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H54'] = - ((df['low'] - df['close']) * df['open'].pow(5)) / ((df['low'] - df['high']) * df['close'].pow(5))
    df[factor_name] = df['H54']
    df.drop(columns=['H54'], errors='ignore', inplace=True)

    return df

def signal(*args):
    # G46 indicator (inverse of the average of four moving averages)
    # Formula: G46 = (MEAN(CLOSE,3)+MEAN(CLOSE,6)+MEAN(CLOSE,12)+MEAN(CLOSE,24))/(4*CLOSE)
    # Average of the 3-, 6-, 12- and 24-day moving averages of close, divided by 4x current close.
    # Above 1 means the blended average sits above current price; below 1 means it sits below.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    numerator = df['close'].rolling(3).mean() + df['close'].rolling(6).mean() + df['close'].rolling(12).mean() + df[ 'close'].rolling(24).mean()
    df['G46'] = numerator / (4 * df['close'])
    df[factor_name] = df['G46']
    df.drop(columns=['G46'], errors='ignore', inplace=True)

    return df

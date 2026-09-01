eps = 1e-8


def signal(*args):
    # H101 indicator (intrabar body-to-range ratio)
    # Formula: H101 = ((CLOSE - OPEN) / ((HIGH - LOW) + .001))
    # (close - open) divided by the day's high-low range.
    # Close to +1 means the bar closed near its high after opening near its low (strong up bar); close to -1 is the mirror image.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['H101'] = (df['close']-df['open'])/((df['high'] - df['low'] + eps) + 0.001)
    df[factor_name] = df['H101']
    df.drop(columns=['H101'], errors='ignore', inplace=True)

    return df

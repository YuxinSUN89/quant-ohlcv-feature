import pandas as pd


def signal(*args):
    # G82 indicator (smoothed Williams %R-style oscillator, longest window)
    # Formula: G82 = SMA((TSMAX(HIGH,6)-CLOSE)/(TSMAX(HIGH,6)-TSMIN(LOW,6))*100,20,1
    # Same construction as G47/G72 smoothed over 20 periods — the slowest of the three variants.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['temp1'] = df['high'].rolling(6, min_periods=1).apply(lambda x: pd.Series(x).max()) - df['close']
    df['temp2'] = (df['high'].rolling(6, min_periods=1).apply(lambda x: pd.Series(x).max()) - df['low'].rolling(6,min_periods=1).apply(lambda x: pd.Series(x).min())) * 100
    df['G82'] = (df['temp1'] / df['temp2']).ewm(alpha=1 / 20, adjust=False).mean()
    df[factor_name] = df['G82']
    df.drop(columns=['temp1', 'temp2', 'G82'], errors='ignore', inplace=True)

    return df

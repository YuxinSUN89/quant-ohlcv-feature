import numpy as np


def signal(*args):
    # G160 indicator (smoothed down-day volatility)
    # Formula: G160 = SMA((CLOSE<=DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)
    # A smoothed series that is the 20-day close std on down days and zero on up days.
    # Rises when down moves are accompanied by elevated price volatility.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['A'] = np.where(df['close'] <= df['close'].shift(1), df['close'].rolling(20).std(ddof=0), 0)
    df['G160'] = df['A'].ewm(alpha=1.0 / 20, adjust=False).mean()
    df[factor_name] = df['G160']
    df.drop(columns=['A', 'G160'], errors='ignore', inplace=True)

    return df

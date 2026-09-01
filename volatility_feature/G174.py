import numpy as np


def signal(*args):
    # G174 indicator (smoothed up-day volatility)
    # Formula: G174 = SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)
    # A smoothed series that is the 20-day close std on up days and zero on down days (mirror of G160).
    # Rises when up moves are accompanied by elevated price volatility.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G174_pre'] = np.where(df['close'] > df['close'].shift(1), df['close'].rolling(20).std(), 0)
    df['G174'] = df['G174_pre'].ewm(alpha=1.0 / 20).mean()
    df[factor_name] = df['G174']
    df.drop(columns=['G174_pre', 'G174'], errors='ignore', inplace=True)

    return df

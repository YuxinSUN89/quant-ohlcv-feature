import numpy as np


def signal(*args):
    # G23 indicator (share of volatility coming from up days)
    # Formula: G23 = SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE:20),0),20,1)/( SMA((CLOSE>DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1)+ SMA((CLOSE<=DELAY(CLOSE,1)?STD(CLOSE,20):0),20,1) )*100
    # Smoothed 20-day close std on up days, expressed as a fraction of (up-day std + down-day std).
    # Above 50 means recent price volatility has concentrated more on up days than down days.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g23_1'] = df['close'].rolling(20, min_periods=1).std()
    df['g23_0'] = df['close'].shift()
    df['gtja23_1'] = np.where((df['close'] > df['g23_0']), df['g23_1'], 0)
    df['gtja23_1'] = df['gtja23_1'].ewm(alpha=1.0 / 20).mean()
    df['gtja23_2'] = np.where((df['close'] <= df['g23_0']), df['g23_1'], 0)
    df['gtja23_2'] = df['gtja23_2'].ewm(alpha=1.0 / 20).mean()
    df['G23'] = df['gtja23_1'] / (df['gtja23_1'] + df['gtja23_2']) * 100
    df[factor_name] = df['G23']
    df.drop(columns=['g23_1', 'g23_0', 'gtja23_1', 'gtja23_2', 'G23'], errors='ignore', inplace=True)

    return df

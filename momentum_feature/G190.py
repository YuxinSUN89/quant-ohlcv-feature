import numpy as np


def signal(*args):
    # G190 indicator (log-odds of beating vs. missing a smoothed return target)
    # Formula: G190 = LOG((COUNT(CLOSE/DELAY(CLOSE)-1>((CLOSE/DELAY(CLOSE,19))^(1/20)-1),20)-1)(SUMIF(((CLOSE/DELAY(CLOSE)-1-(CLOSE/DELAY(CLOSE,19))^(1/20)-1))^2,20,CLOSE/DELAY(CLOSE)-1<(CLOSE/DELAY(CLOSE,19))^(1/20)-1))/((COUNT((CLOSE/DELAY(CLOSE)-1<(CLOSE/DELAY(CLOSE,19))^(1/20)-1),20))(SUMIF((CLOSE/DELAY(CLOSE)-1-((CLOSE/DELAY(CLOSE,19))^(1/20)-1))^2,20,CLOSE/DELAY(CLOSE)-1>(CLOSE/DELAY(CLOSE,19))^(1/20)-1))))
    # Compares how often, and by how much, returns beat vs. missed a smoothed 19-day annualized-style benchmark, expressed as a log ratio.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G190_A'] = df['close'] / df['close'].shift() - 1
    df['G190_B'] = np.power(df['close'] / df['close'].shift(19), 1 / 20) - 1
    df['G190_X'] = np.where(df['G190_A'] > df['G190_B'], 1, 0)
    df['G190_X'] = df['G190_X'].rolling(20, min_periods=1).sum() - 1
    df['G190_Y'] = np.where(df['G190_A'] < df['G190_B'], np.power(df['G190_A'] - df['G190_B'], 2), 0)
    df['G190_Y'] = df['G190_Y'].rolling(20, min_periods=1).sum()
    df['G190_Z1'] = np.where(df['G190_A'] < df['G190_B'], 1, 0)
    df['G190_Z1'] = df['G190_Z1'].rolling(20, min_periods=1).sum()
    df['G190_Z2'] = np.where(df['G190_A'] > df['G190_B'], np.power(df['G190_A'] - df['G190_B'], 2), 0)
    df['G190_Z2'] = df['G190_Z2'].rolling(20, min_periods=1).sum()
    df['G190'] = df['G190_X'] * df['G190_Y'] / (df['G190_Z1'] * df['G190_Z2'])
    df['G190'] = df['G190'].replace([np.inf, -np.inf], np.nan)
    df[factor_name] = df['G190']
    df.drop(columns=['G190_A', 'G190_B', 'G190_X', 'G190_Y', 'G190_Z1', 'G190_Z2', 'G190'], errors='ignore', inplace=True)

    return df

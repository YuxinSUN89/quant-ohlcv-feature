import numpy as np


def signal(*args):
    # G98 indicator (flat-trend mean reversion vs. momentum switch)
    # Formula: G98 = ((((DELTA((SUM(CLOSE, 100) / 100), 100）/DELAY(CLOSE, 100)) < 0.05) || ((DELTA((SUM(CLOSE, 100) / 100), 100)/DELAY(CLOSE,100)) == 0.05))?(-1*(CLOSE - TSMIN(CLOSE, 100))):(-1 * DELTA(CLOSE, 3)))
    # When the 100-day trend has been nearly flat, reverts to distance from the 100-day low; otherwise follows the 3-day price change.
    # A regime-switching factor between mean-reversion (flat markets) and momentum (trending markets).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G98_A'] = (df['close'].rolling(100).sum() / 100).diff(100)
    df['G98_B'] = df['close'].shift(100)
    df['G98_A/B'] = False
    df.loc[((df['G98_A'] / df['G98_B'] < 0.05) | (df['G98_A'] / df['G98_B'] == 0.05)), 'G98_A/B'] = True
    df['G98_C'] = (-1) * (df['close'] - df['close'].rolling(100).min())
    df['G98_D'] = (-1) * df['close'].diff(3)
    df['G98_out'] = np.where(df['G98_A/B'], df['G98_C'], df['G98_D'])
    df['G98'] = df['G98_out']
    df[factor_name] = df['G98']
    df.drop(columns=['G98_A', 'G98_B', 'G98_A/B', 'G98_C', 'G98_D', 'G98_out', 'G98'], errors='ignore', inplace=True)

    return df

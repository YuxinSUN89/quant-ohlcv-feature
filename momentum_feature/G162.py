import numpy as np


def signal(*args):
    # G162 indicator (normalized RSI-style oscillator)
    # Formula: G162 = (SMA(MAX(CLOSE-DELAY(CLOSE,1),0),12,1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),12,1)*100-MIN(SMA(MAX(CLOS E-DELAY(CLOSE,1),0),12,1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),12,1)*100,12))/(MAX(SMA(MAX(CLOSE-DELAY(C LOSE,1),0),12,1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),12,1)*100,12)-MIN(SMA(MAX(CLOSE-DELAY(CLOSE,1),0),12, 1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),12,1)*100,12))
    # Rescales a 12-period smoothed up/down ratio to a 0-1 range using its own 12-day min/max.
    # Near 1 means the underlying up/down ratio is at a local high; near 0 means it is at a local low.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['diff'] = df['close'].diff(1)
    df['max_diff'] = np.where(df['diff'] > 0, df['diff'], 0)
    df['abs_diff'] = abs(df['diff'])
    df['ratio'] = df['max_diff'].ewm(alpha=1 / 12).mean() / df['abs_diff'].ewm(alpha=1 / 12).mean() * 100
    df['part1'] = df['ratio'] - df['ratio'].rolling(12, min_periods=1).min()
    df['part2'] = df['ratio'].rolling(12, min_periods=1).max() - df['ratio'].rolling(12, min_periods=1).min()
    df['G162'] = df['part1'] / df['part2']
    df[factor_name] = df['G162']
    df.drop(columns=['diff', 'max_diff', 'abs_diff', 'ratio', 'part1', 'part2', 'G162'], errors='ignore', inplace=True)

    return df

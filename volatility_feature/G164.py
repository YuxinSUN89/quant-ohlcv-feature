import numpy as np


def signal(*args):
    # G164 indicator (smoothed inverse-move range ratio)
    # Formula: G164 = SMA((((CLOSE>DELAY(CLOSE,1))?1/(CLOSE-DELAY(CLOSE,1)):1)-MIN(((CLOSE>DELAY(CLOSE,1))?1/(CLOSE-DELAY(CLOSE,1)):1),12))/(HIGH-LOW)*100,13,2)
    # A smoothed measure of how the inverse of the day's price move compares to its own 12-day minimum, scaled by the day's range.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g164_0'] = df['close'].shift()
    condition1 = df['close'] > df['g164_0']
    df['G164_prepare_1'] = np.where(condition1, 1 / (df['close'] - df['g164_0']), 1)
    df['G164_prepare_2'] = df['G164_prepare_1'] - df['G164_prepare_1'].rolling(12, min_periods=1).min() / ( df['close'] - df['low'])
    df['G164'] = df['G164_prepare_2'].ewm(alpha=2 / 13, adjust=False).mean()
    df[factor_name] = df['G164']
    df.drop(columns=['g164_0', 'G164_prepare_1', 'G164_prepare_2', 'G164'], errors='ignore', inplace=True)

    return df

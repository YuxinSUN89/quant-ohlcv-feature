import numpy as np


def signal(*args):
    # G49 indicator (directional-movement share (ADX-style, no-gap variant))
    # Formula: G49 = SUM(((HIGH+LOW)>=(DELAY(HIGH,1)+DELAY(LOW,1))?0:MAX(ABS(HIGH-DELAY(HIGH,1)),ABS(LOW-DELAY(LOW,1)))),12)/(SUM(((HIGH+LOW)>=(DELAY(HIGH,1)+DELAY(LOW,1))?0:MAX(ABS(HIGH-DELAY(HIGH,1)),ABS(LOW-DELAY(LOW,1)))),12)+SUM(((HIGH+LOW)<=(DELAY(HIGH,1)+DELAY(LOW,1))?0:MAX(ABS(HIGH-DELAY(HIGH,1)),ABS(LOW-DELAY(LOW,1)))),12))
    # Share of total directional movement (up-range vs. down-range) attributable to up moves over 12 days, only counting days where the high+low range expanded.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['diff_high'] = abs(df['high'] - df['high'].shift())
    df['diff_low'] = abs(df['low'] - df['low'].shift())
    df['Max_diff'] = df[['diff_high', 'diff_low']].max(axis=1)
    condition_1 = (df['high'] + df['low']) >= (df['high'].shift() + df['low'].shift())
    df['v_A_1'] = np.where(condition_1, 0, df['Max_diff'])
    df['value_A'] = df['v_A_1'].rolling(12, min_periods=1).sum()
    condition_2 = (df['high'] + df['low']) <= (df['high'].shift() + df['low'].shift())
    df['v_B_1'] = np.where(condition_2, 0, df['Max_diff'])
    df['value_B'] = df['v_B_1'].rolling(12, min_periods=1).sum()
    df['G49'] = df['value_A'] / (df['value_A'] + df['value_B'])
    df[factor_name] = df['G49']
    df.drop(columns=['diff_high', 'diff_low', 'Max_diff', 'v_A_1', 'value_A', 'v_B_1', 'value_B', 'G49'], errors='ignore', inplace=True)

    return df

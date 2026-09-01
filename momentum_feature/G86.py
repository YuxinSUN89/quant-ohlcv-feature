import numpy as np


def signal(*args):
    # G86 indicator (acceleration/deceleration regime switch)
    # Formula: G86 = ((0.25 < (((DELAY(CLOSE, 20) - DELAY(CLOSE, 10)) / 10) - ((DELAY(CLOSE, 10) - CLOSE) / 10))) ? (-1 * 1) :(((((DELAY(CLOSE, 20)-DELAY(CLOSE, 10)) / 10) ((DELAY(CLOSE, 10) - CLOSE) / 10)) < 0) ? 1 : (( -1 * 1) * (CLOSE - DELAY(CLOSE, 1)))))
    # Compares the change in 10-day momentum over two consecutive 10-day windows to detect strong deceleration or acceleration, else falls back to the 1-day price change.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['close_delay_20'] = df['close'].shift(20)
    df['close_delay_10'] = df['close'].shift(10)
    df['part1'] = (df['close_delay_20'] - df['close_delay_10']) / 10
    df['part2'] = (df['close_delay_10'] - df['close']) / 10
    conditionA = 0.25 < (df['part1'] - df['part2'])
    conditionB = (df['part1'] - df['part2']) < 0
    df['G86_part2'] = np.where(conditionB, 1, -(df['close'] - df['close'].shift(1)))
    df['G86'] = np.where(conditionA, -1, df['G86_part2'])
    df[factor_name] = df['G86']
    df.drop(columns=['close_delay_20', 'close_delay_10', 'part1', 'part2', 'G86_part2', 'G86'], errors='ignore', inplace=True)

    return df

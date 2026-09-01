import numpy as np


def signal(*args):
    # G122 indicator (rate of change of a triple-smoothed log price (TRIX-style))
    # Formula: G122 = (SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2)-DELAY(SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2),1))/DELAY(SMA(SMA(SMA(LOG(CLOSE),13,2),13,2),13,2),1)
    # Percentage change of a three-times EMA-smoothed log(close), similar in spirit to the TRIX oscillator.
    # Positive values indicate the smoothed trend is still rising; negative values indicate it has turned down.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['sma'] = np.log(df['close']).ewm(alpha=2 / 13).mean().ewm(alpha=2 / 13).mean().ewm(alpha=2 / 13).mean()
    df['G122'] = df['sma'].diff() / df['sma'].shift(1)
    df[factor_name] = df['G122']
    df.drop(columns=['sma', 'G122'], errors='ignore', inplace=True)

    return df

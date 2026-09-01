import numpy as np


def signal(*args):
    # G116 indicator (linear-regression slope of price vs. time)
    # Formula: G116 = REGBETA(CLOSE, SEQUENCE, 20)
    # Regression coefficient (beta) of CLOSE against a simple time index over a 20-period window.
    # Positive values indicate an uptrend in the window; negative values indicate a downtrend.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 20
    SEQUENCE = np.arange(1, n + 1)
    df['G116'] = df['close'].rolling(n).apply(lambda x: np.polyfit(SEQUENCE, x.tolist(), deg=1)[0])
    df[factor_name] = df['G116']
    df.drop(columns=['G116'], errors='ignore', inplace=True)

    return df

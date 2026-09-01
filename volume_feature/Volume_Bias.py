# Volume_Bias indicator (short-term vs long-term volume ratio)
# Formula: result = MA(QUOTE_VOLUME, N/24) / MA(QUOTE_VOLUME, N) - 1
# Compares recent short-window (N/24) average volume to the longer N-period average.
# Positive values indicate a recent volume surge relative to the longer baseline (heightened activity).
def signal(*args):
    df = args[0]
    n = args[1]
    factor_name = args[2]

    short_window = max(1, n // 24)
    df[factor_name] = df['quote_volume'].rolling(short_window, min_periods=1).mean() / df['quote_volume'].rolling(n, min_periods=1).mean() -1

    return df

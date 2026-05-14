import numpy as np


def signal(df, n, factor_name, config):
    # Grid indicator (z-score grid position percentage change)
    # Formula: MA = MA(CLOSE,N); STD = STD(CLOSE,N)
    #          GRID = MA((CLOSE - MA) / STD, N)  (rolling mean of z-scores)
    #          result = GRID.pct_change(N)
    # Measures the N-period rate of change of the smoothed z-score position.
    # Captures acceleration of price relative to its own volatility band.
    df["median"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["grid"] = (df["close"] - df["median"]) / df["std"]
    df["grid"] = df["grid"].replace([np.inf, -np.inf], np.nan)
    df["grid"].fillna(value=0, inplace=True)
    df["grid"] = df["grid"].rolling(window=n, min_periods=config.min_periods).mean()
    # pct_change with denominator floor: avoids FP amplification when rolling-mean-of-zscores ≈ 0
    grid_arr = df["grid"].to_numpy(dtype=float)
    prev = np.concatenate([[np.nan] * n, grid_arr[:-n]])
    df[factor_name] = (grid_arr - prev) / np.where(np.abs(prev) > 1e-9, prev, np.nan)
    # df['gridInt'] = df['grid'].astype("int")
    # df[factor_name] = df['gridInt'].pct_change(n)

    del df["median"], df["std"], df["grid"]  # , df['gridInt']

    return df

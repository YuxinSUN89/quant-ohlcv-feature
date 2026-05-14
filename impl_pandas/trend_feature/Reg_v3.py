import numpy as np


def signal(df, n, factor_name, config):
    # Reg_v3 indicator (Close vs OLS linear regression)
    # Formula: OLS fit of CLOSE over N time steps; REG = predicted value at last step (y = ax + b)
    #          result = CLOSE / (REG + eps) - 1
    # Uses closed-form OLS (no sklearn/polyfit) for numerically stable rolling regression.
    # Positive values indicate close is above the fitted trend; negative below.
    eps = config.eps

    def reg_ols(y_arr):
        """Return predicted value at last point from closed-form OLS (no SVD, no sklearn)."""
        m = len(y_arr)
        if m < 2:
            return y_arr[-1]
        x = np.arange(m, dtype=float)
        x_mean = (m - 1) / 2.0
        y_mean = y_arr.mean()
        slope = np.dot(x - x_mean, y_arr - y_mean) / (np.dot(x - x_mean, x - x_mean) + eps)
        intercept = y_mean - slope * x_mean
        return slope * (m - 1) + intercept

    df["reg_close"] = df["close"].rolling(n, min_periods=config.min_periods).apply(reg_ols, raw=True)
    df[factor_name] = df["close"] / (df["reg_close"] + eps) - 1

    # remove redundant columns
    del df["reg_close"]

    return df

import numpy as np
from sklearn.linear_model import LinearRegression


def signal(df, n, factor_name, config):
    # Reg_v3 indicator (Close vs OLS linear regression using sklearn)
    # Formula: OLS fit of CLOSE over N time steps; REG = predicted value at last step (y = ax + b)
    #          result = CLOSE / (REG + eps) - 1
    # Uses sklearn LinearRegression to compute an N-period rolling OLS fit,
    # taking the fitted value at the last point as the regression baseline.
    # Positive values indicate close is above the fitted trend; negative below.
    eps = config.eps

    # sklearn linear regression
    def reg_ols(_y):
        m = len(_y)
        _x = np.arange(m) + 1
        model = LinearRegression().fit(_x.reshape(-1, 1), _y)  # linear regression training
        y_pred = model.coef_ * _x + model.intercept_  # y = ax + b
        return y_pred[-1]

    df["reg_close"] = df["close"].rolling(n, min_periods=config.min_periods).apply(lambda y: reg_ols(y), raw=False)
    df[factor_name] = df["close"] / (df["reg_close"] + eps) - 1

    # remove redundant columns
    del df["reg_close"]

    return df

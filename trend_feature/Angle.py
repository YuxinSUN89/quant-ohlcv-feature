import talib as ta


def signal(df, n, factor_name, config):
    # Angle indicator (Linear Regression Angle of close)
    # Formula: result = LINEARREG_ANGLE(CLOSE, N)
    # Computes the angle of the linear regression line fitted to close prices over N periods.
    # Positive angles indicate upward-sloping trend; negative angles indicate downward-sloping trend.
    df[factor_name] = ta.LINEARREG_ANGLE(df["close"], timeperiod=n)

    # remove redundant columns

    return df

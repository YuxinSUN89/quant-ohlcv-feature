import talib as ta


def signal(df, n, factor_name, config):
    # Reg indicator (Close vs linear regression)
    # Formula: REG = LINEARREG(CLOSE, N); result = CLOSE / REG - 1
    # Measures the deviation of close from its N-period linear regression value.
    # Positive values indicate close is above the regression line (overextended upward); negative below.
    df["reg_close"] = ta.LINEARREG(df["close"], timeperiod=n)  # talib built-in linear regression
    df[factor_name] = df["close"] / df["reg_close"] - 1

    # remove redundant columns
    del df["reg_close"]

    return df

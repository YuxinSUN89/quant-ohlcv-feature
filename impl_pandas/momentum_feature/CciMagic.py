def signal(df, n, factor_name, config):
    # CciMagic indicator (Modified CCI using MA of OHLC prices)
    # Formula: TP = (MA(HIGH,N) + MA(LOW,N) + MA(CLOSE,N)) / 3
    #          MA_TP = MA(TP, N); MD = MA(|MA_TP - MA(CLOSE,N)|, N)
    #          result = (TP - MA_TP) / (0.015 * MD)
    # A smoothed CCI variant where both H, L, C are first averaged over N periods before computing CCI.
    # This reduces noise compared to standard CCI computed on raw prices.

    # calculate modified CCI indicator
    df["open"].rolling(n, min_periods=config.min_periods).mean()  # noqa: F841
    high_ma = df["high"].rolling(n, min_periods=config.min_periods).mean()
    low_ma = df["low"].rolling(n, min_periods=config.min_periods).mean()
    close_ma = df["close"].rolling(n, min_periods=config.min_periods).mean()
    tp = (high_ma + low_ma + close_ma) / 3
    ma = tp.rolling(n, min_periods=config.min_periods).mean()
    md = abs(ma - close_ma).rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = (tp - ma) / md / 0.015

    return df

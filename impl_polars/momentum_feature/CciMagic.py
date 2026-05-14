import polars as pl


def signal(df, n, factor_name, config):
    # CciMagic indicator (Modified CCI using MA of OHLC prices)
    # Formula: TP = (MA(HIGH,N) + MA(LOW,N) + MA(CLOSE,N)) / 3
    #          MA_TP = MA(TP, N); MD = MA(|MA_TP - MA(CLOSE,N)|, N)
    #          result = (TP - MA_TP) / (0.015 * MD)
    # A smoothed CCI variant where both H, L, C are first averaged over N periods before computing CCI.
    # This reduces noise compared to standard CCI computed on raw prices.

    # calculate modified CCI indicator
    df["open"].rolling_mean(n, min_samples=config.min_periods)  # noqa: F841
    high_ma = df["high"].rolling_mean(n, min_samples=config.min_periods)
    low_ma = df["low"].rolling_mean(n, min_samples=config.min_periods)
    close_ma = df["close"].rolling_mean(n, min_samples=config.min_periods)
    tp = (high_ma + low_ma + close_ma) / 3
    ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = abs(ma - close_ma).rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, ((tp - ma) / md / 0.015)))

    return df

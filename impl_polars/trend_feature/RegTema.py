import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # RegTema indicator (TEMA vs its linear regression)
    # Formula: EMA1 = EMA(CLOSE,N); EMA2 = EMA(EMA1,N); EMA3 = EMA(EMA2,N)
    #          TEMA = 3*EMA1 - 3*EMA2 + EMA3; REG_TEMA = LINEARREG(TEMA,N)
    #          result = TEMA / (REG_TEMA + eps) - 1
    # Measures how far the triple exponential MA has deviated from its own linear trend.
    # Positive values indicate TEMA is above its regression line (upward momentum); negative below.
    eps = config.eps
    ema = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    emax2 = ema.ewm_mean(span=n, adjust=config.ewm_adjust)
    emax3 = emax2.ewm_mean(span=n, adjust=config.ewm_adjust)
    tema = 3 * ema - 3 * emax2 + emax3

    # calculate regression
    reg_tema = ta.LINEARREG(tema, timeperiod=n)  # talib built-in linear regression
    df = df.with_columns(pl.Series(factor_name, tema / (reg_tema + eps) - 1))

    return df

import numpy as np
import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** Nvi ********************
    # --- NVI --- 099/125
    # N=144
    # NVI_INC=IF(VOLUME<REF(VOLUME,1),1+(CLOSE-REF(CLOSE,1))/CLOSE,1)
    # NVI_INC[0]=100
    # NVI=CUM_PROD(NVI_INC)
    # NVI_MA=MA(NVI,N)
    # NVI is the cumulative percentage price change on days when volume decreases. NVI theory holds that
    # if prices rise while volume shrinks, it indicates large players are dominating the market.
    # NVI can be used to identify markets dominated by large players (price up, volume down).
    # A buy signal is generated when NVI crosses above NVI_MA;
    # a sell signal is generated when NVI crosses below NVI_MA.

    nvi_inc = np.where(
        df["volume"] < df["volume"].shift(1),
        1 + (df["close"] - df["close"].shift(1)) / (config.normalize_eps + df["close"]),
        1,
    )
    nvi_inc = pl.Series(nvi_inc).fill_nan(None)
    nvi_inc[0] = 100
    nvi = pl.Series(nvi_inc).cum_prod()
    nvi_ma = nvi.rolling_mean(n, min_samples=config.min_periods)

    s = nvi - nvi_ma
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

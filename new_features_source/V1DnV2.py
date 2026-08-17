"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import pandas as pd
import numpy as np

# 财务因子列：此列表用于存储财务因子相关的列名称  
fin_cols = []  # 财务因子列，配置后系统会自动加载对应的财务数据

def add_factor(df: pd.DataFrame, param=None, **kwargs) -> pd.DataFrame:
    """
    计算并将新的因子列添加到股票行情数据中，并返回包含计算因子的DataFrame及其聚合方式。

    工作流程：
    1. 根据提供的参数计算股票的因子值。
    2. 将因子值添加到原始行情数据DataFrame中。

    :param df: pd.DataFrame，包含单只股票的K线数据，必须包括市场数据（如收盘价等）。
    :param param: 因子计算所需的参数，格式和含义根据因子类型的不同而有所不同。
    :param kwargs: 其他关键字参数，包括：
        - col_name: 新计算的因子列名。
        - fin_data: 财务数据字典，格式为 {'财务数据': fin_df, '原始财务数据': raw_fin_df}，其中fin_df为处理后的财务数据，raw_fin_df为原始数据，后者可用于某些因子的自定义计算。
        - 其他参数：根据具体需求传入的其他因子参数。
    :return:
        - pd.DataFrame: 包含新计算的因子列，与输入的df具有相同的索引。

    注意事项：
    - 如果因子的计算涉及财务数据，可以通过`fin_data`参数提供相关数据。
    """

    """    
    ----->>>  配置方法  <<<-----
    配置：('V1DnV2', is_sort_asc, n, arg)
    含义：mtm_mean = MA(收盘价 / 昨日收盘价 - 1, n), atr = MA(MAX(最高价 - 最低价, abs(最高价 - 昨日收盘价), abs(最低价 - 昨日收盘价), n)
        wd_atr = atr / MA(n) * 1e3, mtm_l = 最低价 / 最低价.shift(n) -1, mtm_h = 最高价 / 最高价.shift(n) -1, mtm_c = 收盘价 / 收盘价.shift(n) -1, 
        mtm_atr = MA(MAX(mtm_h - mtm_l, abs(mtm_h - mtm_c.shift(1)), abs(mtm_l - mtm_c.shift(1)), n) * 1e3
        mtm_atr_mean = MA(MAX(MA(mtm_h, n) - MA(mtm_l, n), abs(MA(mtm_h, n) - MA(mtm_c, n).shift(1)), abs(MA(mtm_l, n) - MA(mtm_c, n).shift(1)), n) * 1e3
        V1 = mtm_mean * wd_atr * mtm_atr * mtm_atr_mean, dn1 = MA(V1, n) - STD(V1, n) * MA(abs(V1 - MA(V1, n)) / STD(V1, n), n)
        V1DnV2 = dn1 - V1
    示例：'factor_list': [
                            ('V1DnV2', True, 20, 1),         # V1DnV2_20
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # ========== 原始计算逻辑开始 ==========

    n1 = n
    mtm = df['收盘价_复权'] / df['收盘价_复权'].shift(n1) - 1
    mtm_mean = mtm.rolling(window=n1, min_periods=1).mean()
    c1 = df['最高价_复权'] - df['最低价_复权']
    c2 = abs(df['最高价_复权'] - df['收盘价_复权'].shift(1))
    c3 = abs(df['最低价_复权'] - df['收盘价_复权'].shift(1))
    tr = np.max(np.array([c1, c2, c3]), axis=0)  # 三个数列取其大值
    atr = pd.Series(tr).rolling(window=n1, min_periods=1).mean()
    avg_price = df['收盘价_复权'].rolling(window=n1, min_periods=1).mean()
    wd_atr = atr / avg_price * 1e3  # === 波动率因子
    mtm_l = df['最低价_复权'] / df['最低价_复权'].shift(n1) - 1
    mtm_h = df['最高价_复权'] / df['最高价_复权'].shift(n1) - 1
    mtm_c = df['收盘价_复权'] / df['收盘价_复权'].shift(n1) - 1
    mtm_c1 = mtm_h - mtm_l
    mtm_c2 = abs(mtm_h - mtm_c.shift(1))
    mtm_c3 = abs(mtm_l - mtm_c.shift(1))
    mtm_tr = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)  # 三个数列取其大值
    mtm_atr = pd.Series(mtm_tr).rolling(window=n1, min_periods=1).mean() * 1e3 # === mtm 波动率因子
    mtm_l_mean = mtm_l.rolling(window=n1, min_periods=1).mean()
    mtm_h_mean = mtm_h.rolling(window=n1, min_periods=1).mean()
    mtm_c_mean = mtm_c.rolling(window=n1, min_periods=1).mean()
    mtm_c1 = mtm_h_mean - mtm_l_mean
    mtm_c2 = abs(mtm_h_mean - mtm_c_mean.shift(1))
    mtm_c3 = abs(mtm_l_mean - mtm_c_mean.shift(1))
    mtm_tr = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)  # 三个数列取其大值
    mtm_atr_mean = pd.Series(mtm_tr).rolling(window=n1, min_periods=1).mean() * 1e3 # === mtm_mean 波动率因子
    indicator = mtm_mean * wd_atr * mtm_atr * mtm_atr_mean
    indicator = pd.Series(indicator)
    median = indicator.rolling(window=n1).mean()
    std = indicator.rolling(n1, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
    z_score = abs(indicator - median) / std
    m1 = pd.Series(z_score).rolling(window=n1).mean()
    dn1 = median - std * m1
    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df[f'V1Dn_v2_{n}'] = dn1 - indicator
    factor_col = df[f'V1Dn_v2_{n}']

    # 清理中间列（如果有）


    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

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
    配置：('AdaptBollingV3', is_sort_asc, n, arg)
    含义：AdaptBollingV3 = 涨跌幅均值 * 价格波动率 * 涨跌幅波动率 * 涨跌幅均值波动率，
        B圈因子转化，参考《因子基本结构总结 和 AdaptBollingv3因子拆解》   https://bbs.quantclass.cn/thread/46931
    示例：'factor_list': [  
                            ('AdaptBollingV3', True, 20, 1),       # AdaptBollingV3_20    
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # ========== 原始计算逻辑开始 ==========
    df['mtm'] = df['收盘价_复权'] / df['收盘价_复权'].shift(n) - 1
    df['mtm_mean'] = df['mtm'].rolling(window=n, min_periods=1).mean()
    # 计算价格真实波幅tr
    df['c1'] = df['最高价_复权'] - df['最低价_复权']
    df['c2'] = abs(df['最高价_复权'] - df['收盘价_复权'].shift(1))
    df['c3'] = abs(df['最低价_复权'] - df['收盘价_复权'].shift(1))
    df['tr'] = df[['c1', 'c2', 'c3']].max(axis=1)
    # 价格真实波幅均值atr
    df['atr'] = df['tr'].rolling(window=n, min_periods=1).mean()
    # 计算收盘价均值
    df['avg_price_'] = df['收盘价_复权'].rolling(window=n, min_periods=1).mean()
    # 计算价格波幅均值与收盘价均值的占比，作为波动率
    df['wd_atr'] = df['atr'] / df['avg_price_']
    # 计算涨跌幅波动率
    df['mtm_l'] = df['最低价_复权'] / df['最低价_复权'].shift(n) - 1
    df['mtm_h'] = df['最高价_复权'] / df['最高价_复权'].shift(n) - 1
    df['mtm_c'] = df['收盘价_复权'] / df['收盘价_复权'].shift(n) - 1
    df['mtm_c1'] = df['mtm_h'] - df['mtm_l']
    df['mtm_c2'] = abs(df['mtm_h'] - df['mtm_c'].shift(1))
    df['mtm_c3'] = abs(df['mtm_l'] - df['mtm_c'].shift(1))
    df['mtm_tr'] = df[['mtm_c1', 'mtm_c2', 'mtm_c3']].max(axis=1)
    # 计算涨跌幅波幅的n周期均值
    df['mtm_atr'] = df['mtm_tr'].rolling(window=n, min_periods=1).mean()
    # 计算涨跌幅均值波动率
    df['mtm_l_mean'] = df['mtm_l'].rolling(window=n, min_periods=1).mean()
    df['mtm_h_mean'] = df['mtm_h'].rolling(window=n, min_periods=1).mean()
    df['mtm_c_mean'] = df['mtm_c'].rolling(window=n, min_periods=1).mean()
    df['mtm_c1'] = df['mtm_h_mean'] - df['mtm_l_mean']
    df['mtm_c2'] = abs(df['mtm_h_mean'] - df['mtm_c_mean'].shift(1))
    df['mtm_c3'] = abs(df['mtm_l_mean'] - df['mtm_c_mean'].shift(1))
    df['mtm_tr'] = df[['mtm_c1', 'mtm_c2', 'mtm_c3']].max(axis=1)
    # 计算涨跌幅均值波幅的n周期均值
    df['mtm_atr_mean'] = df['mtm_tr'].rolling(window=n, min_periods=1).mean()
    indicator = 'mtm_mean'
    df[indicator] = df[indicator] * df['mtm_atr']
    df[indicator] = df[indicator] * df['mtm_atr_mean']
    df[indicator] = df[indicator] * df['wd_atr']
    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    factor_col = df[indicator] * 100000000

    # 清理中间列（如果有）
    df.drop(columns=['mtm', 'mtm_mean', 'c1', 'c2', 'c3', 'tr', 'atr', 'wd_atr', 'mtm_l', 'mtm_h', 'mtm_c', 'mtm_c1',
                     'mtm_c2', 'mtm_c3', 'mtm_tr', 'mtm_atr', 'mtm_l_mean', 'mtm_h_mean', 'mtm_c_mean', 'mtm_atr_mean', 'avg_price_'], inplace=True)

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

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
    配置：('PmoTema', is_sort_asc, n, arg)
    含义：Tema = 3 * EMA(n) - 3 * EMA(EMA(n), n) + EMA(EMA(EMA(n), n), n)
        PmoTema = = MA(MA(MA((Tema - Tema.shift(1)) / Tema.shift(1) * 100, n) * 10, 4 * n), 2 * n)
    示例：'factor_list': [
                            ('PmoTema', True, 20, 1),         # PmoTema_20
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # ========== 原始计算逻辑开始 ==========

    df['ema'] = df['收盘价_复权'].ewm(n, adjust=False).mean()
    df['ema_ema'] = df['ema'].ewm(n, adjust=False).mean()
    df['ema_ema_ema'] = df['ema_ema'].ewm(n, adjust=False).mean()
    df['TEMA'] = 3 * df['ema'] - 3 * df['ema_ema'] + df['ema_ema_ema']
    df['ROC'] = (df['TEMA'] - df['TEMA'].shift(1)) / df['TEMA'].shift(1) * 100  # 用TEMA均线代替原CLOSE
    df['ROC_MA'] = df['ROC'].rolling(n, min_periods=1).mean()  # 均线代替动态移动平均
    df['ROC_MA10'] = df['ROC_MA'] * 10
    df['PMO'] = df['ROC_MA10'].rolling(4 * n, min_periods=1).mean()

    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df[f'PmoTema_{n}'] = df['PMO'].rolling(2 * n, min_periods=1).mean()
    factor_col = df[f'PmoTema_{n}']

    # 清理中间列（如果有）
    del df['ema'], df['ema_ema'], df['ema_ema_ema'], df['TEMA']
    del df['ROC'], df['ROC_MA']
    del df['ROC_MA10']
    del df['PMO']

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

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
    配置：('Adx', is_sort_asc, n, arg)
    含义：n缺省值为14
        MAX_HIGH=IF(HIGH>REF(HIGH,1),HIGH-REF(HIGH,1),0)
        MAX_LOW=IF(REF(LOW,1)>LOW,REF(LOW,1)-LOW,0)
        XPDM=IF(MAX_HIGH>MAX_LOW,HIGH-REF(HIGH,1),0)
        PDM=SUM(XPDM,N)
        XNDM=IF(MAX_LOW>MAX_HIGH,REF(LOW,1)-LOW,0)
        NDM=SUM(XNDM,N)
        TR=MAX([ABS(HIGH-LOW),ABS(HIGH-CLOSE),ABS(LOW-CLOSE)])
        TR=SUM(TR,N)
        DI+=PDM/TR
        DI-=NDM/TR
        ADX 指标计算过程中的 DI+与 DI-指标用相邻两天的最高价之差与最
        低价之差来反映价格的变化趋势。当 DI+上穿 DI-时，产生买入信号；
        当 DI+下穿 DI-时，产生卖出信号。
    示例：'factor_list': [  
                            ('Adx', True, '', 1),       # Adx_14    
                            ('Adx', True, 10, 1),       # Adx_10    
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param) if param else 14

    # ========== 原始计算逻辑开始 ==========
    df['max_high'] = np.where(df['最高价_复权'] > df['最高价_复权'].shift(1), df['最高价_复权'] - df['最高价_复权'].shift(1), 0)
    df['max_low'] = np.where(df['最低价_复权'].shift(1) > df['最低价_复权'], df['最低价_复权'].shift(1) - df['最低价_复权'], 0)
    df['XPDM'] = np.where(df['max_high'] > df['max_low'], df['最高价_复权'] - df['最高价_复权'].shift(1), 0)
    df['PDM'] = df['XPDM'].rolling(n).sum()
    df['XNDM'] = np.where(df['max_low'] > df['max_high'], df['最低价_复权'].shift(1) - df['最低价_复权'], 0)
    df['NDM'] = df['XNDM'].rolling(n).sum()
    df['c1'] = abs(df['最高价_复权'] - df['最低价_复权'])
    df['c2'] = abs(df['最高价_复权'] - df['收盘价_复权'])
    df['c3'] = abs(df['最低价_复权'] - df['收盘价_复权'])
    df['TR'] = df[['c1', 'c2', 'c3']].max(axis=1)
    df['TR_sum'] = df['TR'].rolling(n).sum()
    df['DI+'] = df['PDM'] / df['TR']
    df['DI-'] = df['NDM'] / df['TR']
    df[f'ADX_DI+_bh_{n}'] = df['DI+'].shift(1)
    df[f'ADX_DI-_bh_{n}'] = df['DI-'].shift(1)
    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df[f'Adx_{n}'] = (df['PDM'] + df['NDM']) / df['TR']
    factor_col = df[f'Adx_{n}']

    del  df['max_high'], df['max_low'], df['XPDM'], df['PDM'], df['XNDM'], df['NDM'], df['c1'], df['c2'], df['c3'], df['TR'], df['TR_sum'], df['DI+'], df['DI-']

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

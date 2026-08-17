"""
邢不行｜策略分享会
选股策略框架𝓟𝓻𝓸

版权所有 ©️ 邢不行
微信: xbx1717

本代码仅供个人学习使用，未经授权不得复制、修改或用于商业用途。

Author: 邢不行
"""
import pandas as pd

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
    配置：('M日内N日新高次数', is_sort_asc, n, arg)
    含义：M日内N日新高次数 是指M日范围内，N日破新高次数的总和
    示例：'factor_list': [
                            ('M日内N日新高次数', True, [30, 120], 1),         # '120日内30日新高次数
                        ]
    """    
    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']
    n = int(param[0])
    m = int(param[1])

    # ======================== 计算因子 ===========================
    # 在DataFrame中计算指定周期的涨跌幅，并将其添加到新的一列中
    df[f'前{n}日最髙价'] = df['最高价_复权'].shift().rolling(min_periods=1, window=n).max()
    df[f'是否破{n}日前高'] = (df['收盘价_复权'] > df[f'前{n}日最髙价']).astype(int)
    df[f'{m}日内{n}日新高次数'] = df[f'是否破{n}日前高'].rolling(min_periods=1, window=m).sum()

    factor_col = df[f'{m}日内{n}日新高次数']
    del df[f'前{n}日最髙价'], df[f'是否破{n}日前高']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

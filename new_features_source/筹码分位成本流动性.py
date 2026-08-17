"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import pandas as pd

# 财务因子列：此列表用于存储财务因子相关的列名称
fin_cols = []  # 财务因子列，配置后系统会自动加载对应的财务数据
extra_data = {'stock_chip_distribution': 
              ['后复权价格', '历史最低价', '历史最高价', 
               '5分位成本', '10分位成本', '15分位成本', '20分位成本', '25分位成本', '30分位成本', '35分位成本', 
                '40分位成本', '45分位成本', '50分位成本', '55分位成本', '60分位成本', '65分位成本', '70分位成本', 
                '75分位成本','80分位成本', '85分位成本', '90分位成本', '95分位成本', '加权平均成本', '胜率']}


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
    配置：('筹码分位成本流动性', is_sort_asc, '', arg)
    含义：筹码分位成本流动性 = 各分位成本归一化 - 各分位成本归一化.shift()
    示例：'factor_list': [
                            ('筹码分位成本流动性', True, '', 1),         # 筹码分位成本流动性
                        ]
    """

    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']

    subset_cols = df.columns[df.columns.str.endswith("分位成本")]
    df['分位成本最小值'] = df[subset_cols].apply(lambda row: row.min(), axis=1)
    df['分位成本最大值'] = df[subset_cols].apply(lambda row: row.max(), axis=1)
    df['分位成本流动性'] = 0
    for i in range(5, 100, 5):
        df[f'{i}_分位成本归一化'] = (df[f'{i}分位成本'] - df['分位成本最小值']) / (df['分位成本最大值'] - df['分位成本最小值'])
        df['分位成本流动性'] += df[f'{i}_分位成本归一化'] - df[f'{i}_分位成本归一化'].shift()
    df[col_name] = df['分位成本流动性']
    return df[[col_name]]


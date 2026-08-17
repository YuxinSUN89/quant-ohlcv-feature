"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import pandas as pd

fin_cols = []  # 财务因子列
extra_data = {'5min_close': ['0935', '0940', '0945', '0950', '0955', '1000', '1005', '1010', '1015', '1020',
                             '1025', '1030', '1035', '1040', '1045', '1050', '1055', '1100', '1105', '1110',
                             '1115', '1120', '1125', '1130', '1305', '1310', '1315', '1320', '1325', '1330', '1335',
                             '1340', '1345', '1350', '1355', '1400', '1405', '1410', '1415', '1420', '1425', '1430',
                             '1435', '1440', '1445', '1450', '1455']}


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
    :分钟价格5murn:
        - pd.DataFrame: 包含新计算的因子列，与输入的df具有相同的索引。

    注意事项：
    - 如果因子的计算涉及财务数据，可以通过`fin_data`参数提供相关数据。
    """

    """    
    ----->>>  配置方法  <<<-----
    配置：('分钟价格5m', is_sort_asc, time, arg)
    含义：time时刻的收盘价
    示例：'factor_list': [
                            ('分钟价格5m', True, '0955', 1),         # 9:55的收盘价
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']

    if param not in extra_data['5min_close']:
        raise ValueError(f"参数{param}不在可选范围内，参数需要在{extra_data['5min_close']}之内")

    # 保留对应的数据
    factor_col = df[param]

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

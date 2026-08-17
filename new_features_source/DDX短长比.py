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
ov_cols = ['机构资金买入额', '机构资金卖出额', '大户资金买入额', '大户资金卖出额',]

# noinspection PyUnusedLocal
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
    配置：('DDX短长比', is_sort_asc, [n, m], arg)
    含义： DDX短长比 = n日平均DDX/ m日平均abs(DDX)，其中n<m，表征近期大单动向放大，缺省值n=1,m=20
    示例：'factor_list': [
                            ('DDX短长比', True, '', 1),           # DDX短长比_1_20                          
                            ('DDX短长比', True, [3,30], 1),       # DDX短长比_3_30  
                        ]
    """

    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param[0]) if param else 1      # 缺省值为1
    m = int(param[1]) if param else 20      # 缺省值为20

    # ===计算机构和大户资金净流入
    for _acc_ in ['大户', '机构']:
        df[_acc_ + '资金买入额'].fillna(value=0, inplace=True)
        df[_acc_ + '资金卖出额'].fillna(value=0, inplace=True)
    df['机构资金净流入temp'] = df['机构资金买入额'] - df['机构资金卖出额']
    df['大户资金净流入temp'] = df['大户资金买入额'] - df['大户资金卖出额']

    # DDX计算
    df['DDX'] = (df['机构资金净流入temp'] + df['大户资金净流入temp']) / df['流通市值'] * 1e6
    df[f'DDX_Mean{n}'] = df['DDX'].rolling(window=n, min_periods=1).mean()
    df[f'DDX_abs_Mean{m}'] = abs(df['DDX']).rolling(window=m, min_periods=1).mean()
    df[f'DDX短长比_{n}_{m}'] = df[f'DDX_Mean{n}'] / df[f'DDX_abs_Mean{m}']
    factor_col = df[f'DDX短长比_{n}_{m}']
    del df['机构资金净流入temp'], df['机构资金买入额'], df['机构资金卖出额'], df['大户资金净流入temp'], df['大户资金买入额'], df[
        '大户资金卖出额'], df['DDX'], df[f'DDX_Mean{n}'], df[f'DDX_abs_Mean{m}']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

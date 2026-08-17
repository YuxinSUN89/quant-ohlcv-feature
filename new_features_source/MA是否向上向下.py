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

fin_cols = []  # 财务因子列


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
    配置：('MA是否向上向下', is_sort_asc, [n, m, direction], arg)
    含义：m日内收盘价n日均线是否向上或向下。向上：均线斜率>0且最近3日内逐日增大；向下：均线斜率<0且最近3日内逐日减小
    示例：'factor_list': [
                            ('MA是否向上向下', True, [5, 20, '向上'], 1),       # MA_5的内20日整体向上
                            ('MA是否向上向下', True, [3, 10, '向下'], 1),       # MA_3的内10日整体向下
                        ]
    """

    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n, m, direction = int(param[0]), int(param[1]), param[2]

    # 如果参数不在可选范围：
    if direction not in ['向上', '向下']:
        factor_name = __file__.replace('\\', '/').split('/')[-1].replace('.py', '')
        raise ValueError(f"{factor_name} 因子不支持的参数值：{direction}")

    # ===计算均线
    df[f'MA_{n}'] = df['收盘价_复权'].rolling(n).mean()
    # ===计算均线斜率
    df[f'MA_{n}_{m}日斜率'] = df[f'MA_{n}'].rolling(m).apply(calculate_slope)
    # ===判定是否向上或向下
    if direction == '向上':
        df[f'MA_{n}_{m}日{direction}'] = (
                (df[f'MA_{n}_{m}日斜率'] > 0) &
                (df[f'MA_{n}'] > df[f'MA_{n}'].shift(1)) &
                (df[f'MA_{n}'].shift(1) > df[f'MA_{n}'].shift(2))
        ).astype(int)
    elif direction == '向下':
        df[f'MA_{n}_{m}日{direction}'] = (
                (df[f'MA_{n}_{m}日斜率'] < 0) &
                (df[f'MA_{n}'] < df[f'MA_{n}'].shift(1)) &
                (df[f'MA_{n}'].shift(1) < df[f'MA_{n}'].shift(2))
        ).astype(int)

    factor_col = df[f'MA_{n}_{m}日{direction}']
    del df[f'MA_{n}'], df[f'MA_{n}_{m}日斜率']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

def calculate_slope(series):
    """
    计算斜率
    """
    x = np.arange(len(series))
    y = series.values
    if len(x) < 2:  # 确保数据足够计算斜率
        return np.nan
    slope, _ = np.polyfit(x, y, 1)
    return slope
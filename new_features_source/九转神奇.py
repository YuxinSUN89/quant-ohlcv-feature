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
    配置：('九转神奇', is_sort_asc, param, arg)
    含义： 股票九转神奇的数字
    示例：'factor_list': [
                            ('九转神奇', True, '', 1),              # 九转神奇
                        ]
    """

    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']

    # ======================== 计算因子 ===========================
    df['九转数'] = 0  # 初始化九转数列

    turn_counter = 0  # 初始化九转计数器
    for i in range(4, len(df)):  # 从第5天开始计算，因为我们需要查看4天前的收盘价
        if turn_counter >= 0:
            if df['收盘价_复权'][i] > df['收盘价_复权'][i - 4]:
                turn_counter += 1  # 正向九转数增加

                # 如果正向九转数达到9，则重置为0
                if turn_counter > 9:
                    turn_counter = 1  # 根据描述，重新开始为1

            else:
                # 如果不满足增加条件，则重置正向九转数
                turn_counter = -1  # 开始负向九转数计算

        elif turn_counter < 0:
            if df['收盘价_复权'][i] < df['收盘价_复权'][i - 4]:
                turn_counter -= 1  # 负向九转数减少

                # 如果负向九转数达到-9，则重置为0
                if turn_counter < -9:
                    turn_counter = -1  # 根据描述，重新开始为-1

            else:
                # 如果不满足减少条件，则重置负向九转数
                turn_counter = 1  # 开始正向九转数计算

        # 记录当前的九转数
        df.at[i, '九转数'] = turn_counter

    # 我们这里的市值因子使用总市值的数值
    df[col_name] = df['九转数']

    return df[[col_name]]

"""
邢不行｜策略分享会
选股策略框架𝓟𝓻𝓸

版权所有 ©️ 邢不行
微信: xbx1717

本代码仅供个人学习使用，未经授权不得复制、修改或用于商业用途。

Author: 邢不行
"""
import pandas as pd

fin_cols = []  # 财务因子列

extra_data = {'stock_notices_title': ['公告标题']}


# 原始因子链接：https://bbs.quantclass.cn/thread/60304
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
    配置：('是否4月20日前有年报', is_sort_asc, '', arg)
    含义：是否4月20日前有年报, 在2月-5月输出4月20日前是否有年报,有为1,没有为0,
        *注意每年只在2-5月进行输出，用于4月避险
    示例：'factor_list': [
                            ('是否4月20日前有年报', True, '', 1),              # 是否4月20日前有年报
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']

    # 将公告标题转换为字符串
    df['公告标题str'] = df['公告标题'].astype(str)

    # 首先获取交易日期的月份和日期
    df['月份'] = df['交易日期'].dt.month
    df['日期'] = df['交易日期'].dt.day
    df['年份'] = df['交易日期'].dt.year  # 添加年份列用于分组

    # 创建一个条件，判断日期是否在2月1日至4月20日之间
    early_report_condition = (df['月份'].between(2, 3) | ((df['月份'] == 4) & (df['日期'] <= 20)))

    # 检查公告标题中是否包含"年年度报告"字样且不包含"延期披露"
    has_annual_report = (df['公告标题str'].str.contains('年年度报告') &
                         ~df['公告标题str'].str.contains('延期|推迟|延迟|不能|无法|未按期'))

    # 初始化"是否4月20日前有年报"列
    df['是否4月20日前有年报'] = 0

    # 对于每个符合early_report_condition的日期，如果有年报公告，则标记为1
    df.loc[early_report_condition & has_annual_report, '是否4月20日前有年报'] = 1

    # 确保数据按交易日期排序
    df = df.sort_values(['年份', '交易日期']).reset_index(drop=True)

    # 按年份分组处理，确保标记只在当年的2-5月内传播
    for year, group in df.groupby('年份'):

        # 在当前年份组内，找出2-5月的记录
        feb_may_indices = group[group['月份'].between(2, 5)].index

        if len(feb_may_indices) > 0:
            # 检查当年2-5月内是否有标记为1的记录
            has_report = False
            for idx in sorted(feb_may_indices):  # 确保按时间顺序处理
                if df.loc[idx, '是否4月20日前有年报'] == 1:
                    has_report = True
                elif has_report:
                    df.loc[idx, '是否4月20日前有年报'] = 1

    # 计算近期涨跌幅
    factor_col = df[f'是否4月20日前有年报']

    # 清理中间列（如果有）
    del df['月份'], df['日期'], df['年份'], df['公告标题str'], df['公告标题']

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

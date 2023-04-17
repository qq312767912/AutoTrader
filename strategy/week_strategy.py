#!/usr/bin/env python
# encoding:utf-8
'''
@Project ：quantAlert 
@File    ：week_strategy.py
@IDE     ：PyCharm 
@Author  ：阿毛
@Date    ：2023/4/16 15:29 
@desc    ：最简单的策略demo，给出买卖信号——>整合信号compose_signal——>评估信号
'''
import quote.stock as st
import pandas as pd
import numpy as np
import datetime
import strategy.signal_and_evaluate as ev
import matplotlib.pyplot as plt
# 设置行列不忽略
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

def week_period_strategy(code, time_freq, start_date, end_date):
    """
    周期选股（周四买，周一卖）
    :param code:
    :param time_freq:
    :param start_date:
    :param end_date:
    :return:
    """
    data = st.get_single_price(code, time_freq, start_date, end_date)
    # 新建周期字段
    data['weekday'] = data.index.weekday
    #print(data)
    # 周四买入
    data['buy_signal'] = np.where((data['weekday'] == 3), 1, 0)
    # 周一卖出
    data['sell_signal'] = np.where((data['weekday'] == 0), -1, 0)
    #print(data)
    data = ev.compose_signal(data)  # 整合信号
    #print(data)
    data = ev.calculate_prof_pct(data)  # 计算收益
    #print(data)
    data = ev.calculate_cum_prof(data)  # 计算累计收益率
    #print(data)
    data = ev.caculate_max_drawdown(data)  # 最大回撤
    #print(data)

    return data


if __name__ == '__main__':
    df = week_period_strategy('300059.XSHE', 'daily', '2023-03-01', datetime.date.today())
    print(df[['close', 'signal', 'profit_pct', 'cum_profit']])
    print(df[['close', 'signal', 'profit_pct']].describe())
    data = ev.evaluate_strategy(df)
    df['cum_profit'].plot()
    plt.hist(df['cum_profit'], bins=30)
    plt.show()

    # 查看平安银行最大回撤
    # df = st.get_single_price('000001.XSHE', 'daily', '2006-01-01', '2021-01-01')
    # df = caculate_max_drawdown(df)
    # print(df[['close', 'roll_max', 'daily_dd', 'max_dd']])
    # df[['daily_dd', 'max_dd']].plot()
    # plt.show()

    # 计算夏普比率
    # df = st.get_single_price('000001.XSHE', 'daily', '2006-01-01', '2021-01-01')
    # sharpe = calculate_sharpe(df)
    # print(sharpe)

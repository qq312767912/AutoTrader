#!/usr/bin/env python
# encoding:utf-8
'''
@Project ：quantAlert 
@File    ：signal_and_evaluation_sdk.py
@IDE     ：PyCharm
@Author  ：阿毛
@Date    ：2023/4/16 15:00
@desc    ：
'''

import quote.stock as st
import datetime
import strategy.signal_and_evaluate as ev

data_root = "D:/Desktop/quantAlert/data/"
date = datetime.datetime.now().strftime('%Y-%m-%d')
global_code = '000001.XSHE'
global_startdate = '2023-04-01'

# 获取行情
data = st.get_single_price(global_code,'daily',global_startdate)
print(data)
# 获取涨跌幅
data = st.calculate_change_pct(data)
print(data)

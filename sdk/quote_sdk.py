#!/usr/bin/env python
# encoding:utf-8
'''
@Project ：quantAlert 
@File    ：quote_sdk.py
@IDE     ：PyCharm 
@Author  ：阿毛
@Date    ：2023/4/9 23:33 
@desc    ：
'''
import quote.stock as st
import datetime

data_root = "D:/Desktop/quantAlert/data/"
date = datetime.datetime.now().strftime('%Y-%m-%d')
global_code = '000001.XSHE'
global_startdate = '2023-04-01'

# 单只股票分别按照1m,5m,30m,日线级别数据落地
# 按照上述周期分别读取落地数据
# 落地并读取单只股票财务指标
# 落地并读取单只股票估值指标

# 分别落地指定日期、周期数据
def save_csv_quote(code, freq, startdate):
    '''
    存储指定日期开始的指定周期行情数据
    :param freq:'1m', '5m', '15m', '30m', '60m', '120m', 'xm', '1d', '1w', '1M'
    :param start_date= '2015-01-28 09:00:00'
    :example: save_quote_data('000001.XSHE','1m','2023-03-01')
    '''
    try:
        st.update_daily_price(code,'price',freq,startdate)
    except:
        print("载入行情数据失败...")
        return
    print("载入行情数据成功")

'''
**********
*以下是SDK*
**********
TODO:目前四个周期的起始时间相同,实际上应该按照一定范围区分四个时间存储和读取,待优化
'''
# 单只股票分别按照1m,5m,30m,日线级别数据落地
def load_data(code,startdate=None):
    if startdate is None:
        startdate = global_startdate
    save_csv_quote(code, '1m',  startdate)
    save_csv_quote(code, '5m',  startdate)
    save_csv_quote(code, '30m', startdate)
    save_csv_quote(code, '1d',  startdate)

# 分别读取指定日期、周期落地数据
def get_csv_quote(code,freq,start=None,end=None):
    if end is None:
        end = datetime.datetime.today()
        print(end)
    if start is None:
        start = global_startdate
    data = st.get_csv_price2(code,freq,start,end)
    print(data)

# 使用方式1：手动更新股票数据
get_csv_quote(global_code,'30m')
# 使用方式2：对股票池更新行情数据
stock_list = []
for code in stock_list:
    get_csv_quote(code, '30m')


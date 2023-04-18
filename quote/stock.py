#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import datetime
import time
import os
from jqdatasdk import *
auth('','')

# 设置行列不忽略
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 1000)

# 数据保存路径
data_root = "D:/Desktop/quantAlert/data/"

def get_stock_list():
    '''
    获取所有A股股票列表
    上海证券交易所.XSHG
    深圳证券交易所.XSHE
    :return:stock_list
    '''
    stock_list = list(get_all_securities(['stock']).index)
    return stock_list

def get_single_price(code,time_freq,start_date=None,end_date=None):
    '''
    获取单个股票行情数据
    :param code:
    :param time_freq:
    :param start_date:
    :param end_date:
    :return:
    '''
    # 如果start_date=None，默认为从上市日期开始
    if start_date is None:
        start_date = get_security_info(code).start_date
    if end_date is None:
        end_date = datetime.datetime.today()
    # 获取行情数据
    data = get_price(code, start_date=start_date, end_date=end_date,
                     frequency=time_freq, panel=False)
    return data

def init_db(freq):
    '''
    初始化股票数据库
    :return:
    '''
    # 1.获取所有股票代码
    stocks = get_stock_list()
    # 2.存储到csv文件中
    for code in stocks:
        df = get_single_price(code, freq)
        export_data(df, code, 'price', freq)
        print(code)
        print(df.head())

def get_index_list(index_symbol='000300.XSHG'):
    '''
    获取指数成分股，指数代码查询：https://www.joinquant.com/indexData
    :param index_symbol:指数代码，默认沪深300
    :return:成分股代码
    '''
    stocks = get_index_stocks(index_symbol)
    return stocks

def export_data(data, filename, type, freq, mode=None):
    """
    导出数据，如需追加，则删除重复日期数据
    :param data:
    :param filename:
    :param type: 股票数据类型，可以是：price、finance
    :param mode: a代表追加，none代表默认w写入
    :return:
    """
    file_root = data_root + type + '/' + filename + '_' + freq + '.csv'
    # 索引重命名，因为第一列会是unamed
    data.index.names = ['date']
    if mode == 'a':
        data.to_csv(file_root, mode=mode, header=False)
        # 删除重复值
        data = pd.read_csv(file_root)  # 读取数据
        data = data.drop_duplicates(subset=['date'])  # 以日期列为准
        data.to_csv(file_root, index=False)  # 重新写入
    else:
        data.to_csv(file_root)  # 判断一下file是否存在 > 存在：追加 / 不存在：保持

    print('已成功存储至：', file_root)



def update_daily_price(stock_code, type='price', freq='1d', startdate=None):
    if startdate is None:
        startdate = get_security_info(stock_code).start_date
    # 基于export_data，更新全量数据到今天
    file_root = data_root + type + '/' + stock_code + '_' + freq + '_.csv'
    if os.path.exists(file_root):  # 如果存在对应文件
        # 3.2获取增量数据（code，startsdate=对应股票csv中最新日期，enddate=今天）
        startdate = pd.read_csv(file_root, usecols=['date'])['date'].iloc[-1]
        df = get_single_price(stock_code, freq, startdate, datetime.datetime.today())
        # 3.3追加到已有文件中
        export_data(df, stock_code, 'price',freq, 'a')
    else:
        # 重新获取该股票行情数据
        df = get_single_price(stock_code, freq,startdate)
        export_data(df, stock_code, 'price',freq)

    print("股票数据已经更新成功：", stock_code)

def get_csv_price(code, start_date, end_date, columns=None):
    """
    基于update_daily_price更新到今天的全量数据，取出所需时间区间、所需列，
    :param code: str,股票代码
    :param start_date: str,起始日期
    :param end_date: str,起始日期
    :param columns: list,选取的字段
    :return: dataframe
    """
    # 使用update直接更新
    update_daily_price(code)
    # 读取数据
    file_root = data_root + 'price/' + code + '.csv'
    if columns is None:
        data = pd.read_csv(file_root, index_col='date')
    else:
        data = pd.read_csv(file_root, usecols=columns, index_col='date')
    # print(data)
    # 根据日期筛选股票数据 start\end要为string
    return data[(data.index >= start_date) & (data.index <= end_date)]

def get_csv_price2(code, freq, start_date, end_date, columns=None):
    """
    基于update_daily_price更新到今天的全量数据，取出所需时间区间、所需列，
    :param code: str,股票代码
    :param start_date: str,起始日期
    :param end_date: str,结束日期
    :param columns: list,选取的字段
    :return: dataframe
    """
    # 读取数据
    file_root = data_root + 'price/' + code + '_' + freq +  '.csv'
    if columns is None:
        data = pd.read_csv(file_root, index_col='date')
    else:
        data = pd.read_csv(file_root, usecols=columns, index_col='date')
    # print(data)
    # 根据日期筛选股票数据
    print(start_date)
    print(end_date)
    return data[(data.index >= start_date) & (data.index <= str(end_date))]


def transfer_price_freq(data, time_freq):
    """
    将数据转换为制定周期：开盘价（周期第1天）、收盘价（周期最后1天）、最高价（周期内）、最低价（周期内）
    :param data:
    :param time_freq:
    :return:
    """
    df_trans = pd.DataFrame()
    df_trans['open'] = data['open'].resample(time_freq).first()
    df_trans['close'] = data['close'].resample(time_freq).last()
    df_trans['high'] = data['high'].resample(time_freq).max()
    df_trans['low'] = data['low'].resample(time_freq).min()

    return df_trans


def get_single_finance(code, date, statDate):
    """
    获取单个股票财务指标
    :param code:
    :param date:
    :param statDate:
    :return:
    """
    data = get_fundamentals(query(indicator).filter(indicator.code == code), date=date, statDate=statDate)  # 获取财务指标数据
    return data


def get_single_valuation(code, date, statDate):
    """
    获取单个股票估值指标
    :param code:
    :param date:
    :param statDate:
    :return:
    """
    data = get_fundamentals(query(valuation).filter(valuation.code == code), date=date, statDate=statDate)  # 获取财务指标数据
    return data

def calculate_change_pct(data):
    """
    涨跌幅 = (当期收盘价-前期收盘价) / 前期收盘价
    :param data: dataframe，带有收盘价
    :return: dataframe，带有涨跌幅
    """
    data['close_pct'] = (data['close'] - data['close'].shift(1)) \
                        / data['close'].shift(1)
    return data



if __name__ == '__main__':
    # data = get_fundamentals(query(indicator), statDate='2020')  # 获取财务指标数据
    # print(data)

    # df = get_fundamentals(query(valuation), date='2021-03-24')
    # print(df)

    # 5.3获取沪深300指数成分股代码
    print(get_index_list())
    print(len(get_index_list()))




# coding:utf-8

import os.path as path
import pandas as pd


def asser_msg(condition, msg):
    if not condition:
        raise Exception(msg)


def read_file(filename):
    # 获取文件的绝对路径
    fp = path.join(path.dirname(__file__), filename)

    # 判定文件是否存在
    asser_msg(path.exists(fp), "文件不存在")

    # 读取CSV文件并返回
    return pd.read_csv(fp, index_col=0, parse_dates=TabError, infer_datetime_format=True)


def SMA(values, n):
    """

    :param values:
    :param n:
    :return: 简单滑动平均
    """
    return pd.Series(values).rolling(n).mean()


def crossover(series1, series2):
    """
    检查两个序列是否在结尾交叉
    :param series1: 序列1
    :param series2: 序列2
    :return: 交叉->True;不交叉->False
    """
    return series1[-2] < series2[-2] and series1[-1] > series2[-1]
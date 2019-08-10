# coding:utf-8

import abc
import numpy as np
from typing import Callable


class Strategy(metaclass=abc.ABCMeta):
    """
    抽象策略类，用于定义交易策略。
    如果要定义自己的策略类，需要继承这个基类，并实现两个抽象方法
    Strategy.init
    Strategy.next
    """
    def __init__(self, broker, data):
        """
        构造策略对象
        :param broker: ExchangeAPI  交易API接口用于模拟交易
        :param data:   list         行情数据
        """
        self._broker = broker
        self._data = data
        self._indicators = []
        self._tick = 0

    def I(self, func: Callable, *args) -> np.ndarray:
        """
        计算买卖指标向量。买卖指标向量是一个数组，长度和历史数
        据对呀；用来判定这个时间点需要卖还是买。
        :param func: 可回调的函数
        :param args: 接收的位置参数

        :return: np.ndarry 数据类型
        """
        value = func(*args)
        value = np.asarray(value)
        assert_msg(value.shape[-1] == len(self._data.Close),
                   '指标长度必须和data长度相同')

        self._indicators.append(value)
        return value

    @property
    def tick(self):
        return self._tick

    @abc.abstractmethod
    def init(self):
        """
        初始化策略。在策略回测/执行过程汇总调用一次，用于初始化策略
        内部状态。这里也可以预计算策略的辅助函数。比如根据历史行情数据：
        计算买卖的指标向量；
        训练模型/初始化模型参数
        :return:
        """
        pass

    @abc.abstractmethod
    def next(self, tick):
        """
        步进函数，执行第tick步的策略。tick代表当前的"时间"。比如data[tick]
        用于访问当前的市场价格
        :param tick:
        :return:
        """
        pass

    def buy(self):
        self._broker.buy()

    def sell(self):
        self._broker.sell()

    @property
    def data(self):
        return self._data

from utils import asser_msg, crossover, SMA


class SmaCross(Strategy):
    # 小窗口SMA的窗口大小，用于计算SMA快线
    fast = 30

    # 大窗口SMA的窗口大小，用于计算SMA慢线
    slow = 90

    def init(self):
        # 计算历史上每个时刻的快线和慢线
        self.sma1 = self.I(SMA, self.data.Close, self.fast)
        self.sma2 = self.I(SMA, self.data.Close, self.slow)

    def next(self, tick):
        # 如果快线刚好越过慢线，买入全部
        if crossover(self.sma1[:tick], self.sma1[:tick]):
            self.buy()

        # 如果慢线刚好越过快线，卖出全部
        elif crossover(self.sma2[:tick], self.sma2[:tick]):
            self.sell()

        # 其他情况不进行操作
        else:
            pass

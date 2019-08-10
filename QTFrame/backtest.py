# coding:utf-8

import numpy as np
import pandas as pd

from numbers import Number
from strategy import Strategy, SmaCross
from utils import read_file, asser_msg, crossover, SMA


class ExchangeAPI:
    def __init__(self, data, cash, commission):
        asser_msg(0 < cash, '初始现金大于0，输入现金数量：{}'
                  .format(cash))
        asser_msg(0 <= commission <= 0.05, '合理的手续费不能超过5%，输入手续费：{}'
                  .format(commission))
        self._inital_cash = cash
        self._data = data
        self._commission = commission
        self._position = 0
        self._cash = cash
        self._i = 0

    @property
    def cash(self):
        """
        :return: 返回当前账户的现金数量
        """
        return self._cash

    @property
    def position(self):
        """
        :return: 返回当前的仓位
        """
        return self._position

    @property
    def inital_cash(self):
        """
        :return: 返回初始现金数量
        """
        return self._inital_cash

    @property
    def market_value(self):
        """
        :return: 返回当前市值
        """
        return self._cash + self._position * self.current_price

    @property
    def current_price(self):
        """
        :return: 返回当前市场价格
        """
        return self._data.Close[self._i]

    def buy(self):
        """
        用当前账户剩余资金，按照市场价格全部买入
        """
        self._position = float(self._cash * (1 - self._commission) / self.current_price)
        self._cash = 0.0  # 初始化资金

    def sell(self):
        """
        卖出当前账户剩余持仓
        """
        self._cash += float(self._position * self.current_price * (1 - self._commission))
        self._position = 0.0  # 初始化持仓

    def next(self, tick):
        self._i = tick


class Backtest:
    """
    Backtest 回测类，用于读取历史行情数据、执行策略、模拟交易并估计收益。
    初始化的时候调用Backtest.run来时回测

    instance , `backtesting.backtesting.Backtest.optimize` to optimize it
    """
    def __init__(self,
                 data: pd.DataFrame,
                 strategy_type: type(Strategy),
                 broker_type: type(ExchangeAPI),
                 cash: float = 1000,
                 commission: float = .0):
        """

        :param data:          pandas DataFrame格式的历史OHLCV数据
        :param strategy_type: 交易所API类型，负责执行买卖操作以及账户状态的维护
        :param broker_type:   策略类型
        :param cash:          初始资金数量
        :param commission:    每次交易手续费率，如2%的手续费为0.02
        """
        asser_msg(issubclass(strategy_type, Strategy), 'strategy_type不是Strategy类型')
        asser_msg(issubclass(broker_type, ExchangeAPI), 'broker_type不是ExchangeAPI类型')
        asser_msg(isinstance(commission, Number), 'commission不是浮点数值类型')

        data = data.copy(False)

        # 如果没有Volumn列，填充NaN
        if 'Volume' not in data:
            data['Volume'] = np.nan

        # 验证OHLC数据格式
        asser_msg(len(data.colums & {'Open', 'High', 'Low', 'Close', 'Volume'}) == 5,
                  "输入的`data`格式不正确，至少包含列：'open', 'High','Low', 'Close'")

        # 检查缺失值
        asser_msg(not data[['Open', 'High', 'Low', 'Close']].max().isnull().any(),
                  '部分OHLC包含缺失值，请去掉哪些航或者通过差值填充！')

        # 如果行情数据没有按照时间排序，重新排序一下
        if not data.index.is_monotonic_increasing:
            data = data.sort_index()

        # 利用数据，初始化交易所对象和策略对象。
        self._data = data  # pd.dataframe type data
        self._broker = broker_type(data, cash, commission)
        self._strategy = strategy_type(self._broker, self._data)
        self._result = None

    def run(self) -> pd.Series:
        """
        运行回测，迭代历史数据，执行模拟交易并返回回测结果
        :return:
        """
        strategy = self._strategy
        broker = self._broker

        # 策略初始化
        strategy.init()

        # 设定回测开始和结束位置
        start = 100
        end = len(self._data)

        # 回测主循环，更新市场状态，然后执行策略
        for i in range(start, end):
            broker.next(i)
            strategy.next(i)

        # 完成策略执行之后，计算结果并返回
        self._results = self._compute_result(broker)

        return self._results


    def _compute_result(self, broker):
        s = pd.Series()
        s['初始市值'] = broker.initial_cash
        s['结束市值'] = broker.market_value
        s['收益'] = broker.market_value - broker.initial_cash

        return s

def main():
    BTCUSD = read_file('BTCUSD_GEMINI.csv')
    ret = Backtest(BTCUSD, SmaCross, ExchangeAPI, 10000.0, 0.003).run()
    print(ret)

if __name__ == '__main__':
    main()


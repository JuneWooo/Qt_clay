# coding:utf-8

import copy
import logging

logger = logging.getLogger(__name__)


# 行情处理模块
class OrderBook(object):

    BIDS = 'bid'  # 买方挂单编号
    ASKS = 'ask'  # 卖方挂单编号

    def __init__(self, limit=20):
        self.limit = limit

        # (price, amount)
        self.bids = {}
        self.asks = {}

        # sort process data of price and amount whiches we wanna got
        self.bids_sorted = []
        self.asks_sorted = []

    def insert(self, price, amount, direction):
        if direction == self.BIDS:
            if amount == 0:
                if price in self.bids:
                    del self.bids[price]
            else:
                self.bids[price] = amount
        elif direction == self.ASKS:
            if amount == 0:
                if price in self.asks:
                    del self.asks[price]
            else:
                self.asks[price] = amount
        else:
            logger.warning("WARNING: unknown direction {}".format(direction))

    def sort_and_truncate(self):
        # sort
        self.bids_sorted = sorted([(price, amount) for price, amount in self.bids.items()], reverse=True)
        self.asks_sorted = sorted([(price, amount) for price, amount in self.asks.items()])

        # truncate
        self.bids_sorted = self.bids_sorted[:self.limit]
        self.asks_sorted = self.asks_sorted[:self.limit]

        # copy back to bids and asks
        self.bids = dict(self.bids_sorted)
        self.asks = dict(self.asks_sorted)

    def get_copy_of_bids_and_asks(self):
        logger.info("gemini oderbook data process done...are you wanna trade it now?")
        return copy.deepcopy(self.bids_sorted), copy.deepcopy(self.asks_sorted)

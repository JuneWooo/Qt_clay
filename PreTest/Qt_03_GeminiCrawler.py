# coding:utf-8

import time
import json
import ssl
import websocket
from Qt_03_GeminiOrderbook import OrderBook


# 行情抓取模块
class Crawler:
    def __init__(self, symbol, output_file):
        """
            1.OrderBook的初始化参数limit是用来指示bids,asks（买方执单，
              卖方执单）保留多少条数据，这里我们选择前10条
            2.创建websocket服务, on_message参数对应的回调是类成员函数
              第一个参数是self直接写将会出错，因此利用匿名函数来获取我们
              想要的数据message.
        :param symbol: 标志
        :param output_file: 输出
        """
        self.orderbook = OrderBook(limit=10)
        self.output_file = output_file

        self.ws = websocket.WebSocketApp(
            'wss://api.gemini.com/v1/marketdata/{}'.format(symbol),
            on_message=lambda ws, message: self.on_message(message)
        )
        self.ws.run_forever(sslopt={'cert_requests': ssl.CERT_NONE})

    def on_message(self, message):
        # 对收到的信息进行处理，然后发送给orderbook
        data = json.loads(message)
        for event in data['events']:
            price, amount, directions = float(event['price']), \
                                        float(event['amount']), \
                                        event['side']
            # 插入信息
            self.orderbook.insert(price, amount, directions)

        # 整理 orderbook，排序后只选取我们需要的前几个数据
        self.orderbook.sort_and_truncate()

        # 输出到文件
        with open(self.output_file, 'a+') as f:
            bids, asks = self.orderbook.get_copy_of_bids_and_asks()
            output = {
                'bids': bids,
                'asks': asks,
                'ts': int(time.time() * 1000)
            }
            f.write(json.dumps(output) + '\n')


if __name__ == '__main__':
    crawler = Crawler(symbol="BTCUSD", output_file='BTCUSD.txt')

# coding:utf-8

"""
HTTP发送一次请求（Gemini），等待响应所花费的时间
通过curl 命令查看
In  => curl -w "TCP handshake: %{time_connect}s,
                SSL handshake: %{time_appconnect}s\n"
            -so /dev/null https://www.gemini.com

out => TCP handshake: 0.371051s,
       SSL handshake: 0.986698s
"""

import websocket
import thread
import time
import ssl


# 在接收到服务器发送消息时调用
def on_message(ws, message):
    print ('Received:' + message)


# 在和服务器建立完成连接时调用
def on_open(ws):
    # 线程运行函数
    def gao():
        # 往服务器依次发送 0-4 ，每次发送完休息 0.1 秒
        for i in range(5):
            time.sleep(0.01)
            msg = "{0}".format(i)
            ws.send(msg)
            print('Sent: ' + msg)
        # 休息 1 秒用于接受服务器回复的消息
        time.sleep(1)

        # 关闭 Websocket 的连接
        ws.close()
        print("Websocket closed")

    # 在另一个线程中运行 gao() 函数
    thread.start_new_thread(gao, ())


# 获取Gemini的委托账单
count = 5


def on_message_gemini(ws_ge, message):
    """

    :param ws_ge: gemini 的api请求uri
    :param message: 接收的消息参数，作为本回调函数的返回值
    :return:
    """
    global count
    print(message)
    count -= 1
    # 接收了5次消息之后关闭websocket连接
    if count == 0:
        ws_ge.close()


if __name__ == '__main__':
    ws = websocket.WebSocketApp('ws://echo.websocket.org/',
                                on_message=on_message,
                                on_open=on_open)
    ws.run_forever()

    ws_ge = websocket.WebSocketApp(
        "wss://api.gemini.com/v1/marketdata/btcusd?top_of_book=true&offers=true",
        on_message=on_message_gemini
    )
    ws_ge.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
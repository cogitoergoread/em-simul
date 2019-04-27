import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import datetime
import json


def on_message(ws, message):
    print(message)
    lora = json.loads(message)
    port = lora["port"]
    data = lora["data"]
    ts = lora["ts"]
    time = datetime.datetime.fromtimestamp(ts // 1000)
    timeStr = time.strftime('%Y-%m-%dT%H:%M:%S')
    eui = lora["EUI"]
    print("Lora, Device:{}, Time:{}, Port:{}, Data:{}".format(eui, timeStr, port, data))


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print('OnOpen...')


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        'wss://ah1.connectmedia.hu/app?token=vgEAhQAAABNhaDEuY29ubmVjdG1lZGlhLmh13GsVZpRi0N-ZlAwihv3VwQ==',
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

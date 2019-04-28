import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import datetime
import json
import lora
import paho.mqtt.client as mqtt


class MqttSettings:
    MQTT_HOST = "tick.rubin.hu"
    MQTT_PORT = 1883
    MQTT_KEEPALIVE_INTERVAL = 45
    MQTT_CHANNEL = "ahlora"

def on_message(ws, message):
    print(message)
    loraMsg = json.loads(message)
    port = loraMsg["port"]
    data = loraMsg["data"]
    ts = loraMsg["ts"]
    time = datetime.datetime.fromtimestamp(ts // 1000)
    timeStr = time.strftime('%Y-%m-%dT%H:%M:%S')
    eui = loraMsg["EUI"]
    if loraMsg["cmd"] == "rx":
        dict_msg = lora.Decoder.data_to_dict(data, port)
        dict_msg["pod_name"] = eui
        dict_msg["timestamp"] = timeStr
        msg = json.dumps(dict_msg)
        print('Lora Rx, MQTT,MSG:{}'.format(msg))
        mqttc = mqtt.Client()
        mqttc.connect(MqttSettings.MQTT_HOST, MqttSettings.MQTT_PORT, MqttSettings.MQTT_KEEPALIVE_INTERVAL)
        mqttc.publish(MqttSettings.MQTT_CHANNEL, msg)
        mqttc.disconnect()

    else:
        print("Lora GW, Device:{}, Time:{}, Port:{}, Data:{}".format(eui, timeStr, port, data))



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

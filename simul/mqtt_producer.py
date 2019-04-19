import paho.mqtt.client as mqtt
import json
import pprint
import datetime
import simul


class MqttSettings:
    MQTT_HOST = "localhost"
    MQTT_PORT = 3883
    MQTT_KEEPALIVE_INTERVAL = 45
    MQTT_CHANNEL = "sensors"


class MqttPublish:
    mqttc: mqtt.Client

    def on_publish(client, userdata, mid):
        print("Message Published to MQTT ...")

    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_publish = self.on_publish
        self.mqttc.connect(MqttSettings.MQTT_HOST, MqttSettings.MQTT_PORT, MqttSettings.MQTT_KEEPALIVE_INTERVAL)

    def close(self):
        self.mqttc.disconnect()

    def publish(self, rec: simul.Record):
        measdict = {1: 'Főmérő', 2: 'Szerver', 3: 'Adminn'}

        for logEvent in rec.logok:
            if logEvent.event == simul.EventType.MERES:
                pod = measdict[logEvent.mid]
                timePyt = (datetime.datetime.today().replace(hour=0, minute=0, second=0)
                           + datetime.timedelta(seconds=logEvent.timestamp))
                timestampStr = timePyt.strftime("%Y/%m/%d %H:%M:%S")
                dict_msg = {"pod_name": pod,
                            "consumption": logEvent.value,
                            "timestamp": timestampStr}
                msg = json.dumps(dict_msg)
                print(msg)
                self.mqttc.publish(MqttSettings.MQTT_CHANNEL, msg)

"""
Pilot DC-ből Rubin POD adatokat lekérdez, és felad a MQ TIG stack felé.

Kell egy DC port forward:
 ssh -A  -L 4123:localhost:2123 muszi@smartamr-dc1.rubin.hu

Ekkor le lehet kérdezni a PODot:
http://localhost:4123/dc/client//lastmeasure?deviceid=1018010367&channel=0

Ennek eredménye:
{
    "responseParameters": {
        "success": true,
        "errorCode": null,
        "errorMessage": null
    },
    "deviceID": "1018010367",
    "channel": 0,
    "output": {
        "time": "2019-04-21T11:25:00",
        "value": 188253
    }
}

"""
import json
import requests
import paho.mqtt.client as mqtt


class DcSettings:
    MQTT_HOST = "localhost"
    MQTT_PORT = 3883
    MQTT_KEEPALIVE_INTERVAL = 45
    MQTT_CHANNEL = "sensors"
    POD_LIST = [{'pod': 'Rubin_HVAC_Fazis_3', 'sc': 1015020426, 'ch': 6, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_HVAC_Fazis_2', 'sc': 1015020426, 'ch': 5, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_HVAC_Fazis_1', 'sc': 1015020426, 'ch': 4, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Iroda_Fazis_1', 'sc': 1014100061, 'ch': 5, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Iroda_Fazis_2', 'sc': 1014100061, 'ch': 6, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Iroda_Fazis_3', 'sc': 1014100061, 'ch': 7, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Szerver_Fazis_3', 'sc': 1014100061, 'ch': 4, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Szerver_Fazis_2', 'sc': 1014100061, 'ch': 3, 'off': 0, 'mul': 1000},
                {'pod': 'Rubin_Szerver_Fazis_1', 'sc': 1014100061, 'ch': 2, 'off': 0, 'mul': 1000}
                ]


class DcToMQ:
    mqttc: mqtt.Client

    def on_publish(client, userdata, mid):
        """Logging to MQ, callback"""
        print(f"Message {mid} Published to MQTT ...")

    def __init__(self):
        """Build up MQ connection"""
        self.mqttc = mqtt.Client()
        self.mqttc.on_publish = self.on_publish
        self.mqttc.connect(DcSettings.MQTT_HOST, DcSettings.MQTT_PORT, DcSettings.MQTT_KEEPALIVE_INTERVAL)
        print(self.mqttc)

    def close(self):
        self.mqttc.disconnect()

    def produce(self):
        for podDi in DcSettings.POD_LIST:
            # Get DC
            sc = podDi['sc']
            channel = podDi['ch']
            r = requests.get(f'http://localhost:4123/dc/client/lastmeasure?deviceid={sc}&channel={channel}')
            dcDi = r.json()

            # Publish MQ
            value = dcDi['output']['value'] / podDi['mul']
            pod = podDi['pod']
            dcTime = dcDi['output']['time']
            timestampStr = dcTime.replace('T', ' ')
            timestampStr = timestampStr.replace('-', '/')
            dict_msg = {"pod_name": pod,
                        "consumption": value,
                        "timestamp": timestampStr}
            msg = json.dumps(dict_msg)
            print(msg)
            self.mqttc.publish(DcSettings.MQTT_CHANNEL, msg)


if __name__ == '__main__':
    dmq = DcToMQ()
    dmq.produce()
    dmq.close()

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
    POD_LIST = [
        {'pod': 'Modbus Brutál szerever - Áram Max', 'sc': 1000010012, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Brutál szerever - hatásos telj.', 'sc': 1000010012, 'ch': 4, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Légkezelő hőcserélő bemenet hőmérséklet', 'sc': 1000010011, 'ch': 0, 'off': 30,
         'mul': 10, 'unit': 'Celsius-fok'},
        {'pod': 'Rubin_Gáz', 'sc': 1015020426, 'ch': 7, 'off': 0, 'mul': 100, 'unit': 'm3'},
        {'pod': 'Rubin_Hőmennyiségmérő', 'sc': 1015020426, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'MWh'},
        {'pod': 'Rubin Iroda TIP meddő ', 'sc': 1014100061, 'ch': 1, 'off': 0, 'mul': 250, 'unit': 'kVArh'}
        ]
    MEA_UNIT_CURR = 'A'
    MEA_UNIT_CONS = 'kWh'
    MEA_UNIT_TEMP = 'Celsius-fok'
    MEA_UNIT_GAS = 'm3'
    MEA_UNIT_HEAT = 'MWh'
    MEA_UNIT_REAC = 'kVArh'


class DcToMQ:
    mqttc: mqtt.Client

    def on_publish(client, userdata, mid):
        """Logging to MQ, callback"""
        print(f"Message {mid} Published to MQTT ...")


    def __init__(self):
        """Build up MQ connection"""
        # self.mqttc = mqtt.Client()
        # self.mqttc.on_publish = self.on_publish
        # self.mqttc.connect(DcSettings.MQTT_HOST, DcSettings.MQTT_PORT, DcSettings.MQTT_KEEPALIVE_INTERVAL)
        # print(self.mqttc)
        pass

    def close(self):
        # self.mqttc.disconnect()
        pass

    def produce(self):
        for podDi in DcSettings.POD_LIST:
            # Get DC
            sc = podDi['sc']
            channel = podDi['ch']
            r = requests.get(f'http://localhost:4123/dc/client/lastmeasure?deviceid={sc}&channel={channel}')
            dcDiAct = r.json()

            # Get timestamp
            dcTime = dcDiAct['output']['time']

            # Get previous value
            r = requests.get(f'http://localhost:4123/dc/client/measurevalue?deviceid={sc}&channel={channel}')
            dcDiPrev = r.json()


            # Publish MQ
            value = dcDiAct['output']['value'] / podDi['mul']
            pod = podDi['pod']

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

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

http://localhost:4123/dc/client/measurevalue?deviceid=1000010012&channel=5&time=2019-04-27T07:20:00
{
    "responseParameters": {
        "success": true,
        "errorCode": null,
        "errorMessage": null
    },
    "deviceID": "1000010012",
    "channel": 5,
    "measureValue": {
        "timestamp": "2019-04-27T07:20:00",
        "problem": null,
        "value": 109550667
    }
}
"""
import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

class DcSettings:
    MQTT_HOST = "localhost"
    MQTT_PORT = 3883
    MQTT_KEEPALIVE_INTERVAL = 45
    MQTT_CHANNEL = "sensors"
    DC_PORT = 4123
    POD_LIST = [
        {'pod': 'Modbus Brutál szerever - Áram Max', 'sc': 1000010012, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Brutál szerever - hatásos telj.', 'sc': 1000010012, 'ch': 4, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Csigabiga - hatásos telj.', 'sc': 1000010012, 'ch': 2, 'off': 0, 'mul': 10000, 'unit': 'kWh'},
        {'pod': 'Modbus Csigabiga - Max Áram', 'sc': 1000010012, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 1 - hatásos telj.', 'sc': 1000010010, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 1 - Max Áram', 'sc': 1000010010, 'ch': 1, 'off': 0, 'mul': 1000,
         'unit': 'A'},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 2 - Hatásos telj.', 'sc': 1000010010, 'ch': 2, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 2 - Max Áram', 'sc': 1000010010, 'ch': 3, 'off': 0, 'mul': 1000,
         'unit': 'A'},
        {'pod': 'Modbus Légkezelő hőcserélő bemenet hőmérséklet', 'sc': 1000010011, 'ch': 0, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Légkezelő hőcserélő kimenet hőmérséklet', 'sc': 1000010011, 'ch': 1, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Légkezelő iroda befújt levegő hőmérséklet', 'sc': 1000010011, 'ch': 2, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Légkezelő Iroda elszívott levegő hőmérs.', 'sc': 1000010011, 'ch': 3, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Légkezelő L1  - Áram Max', 'sc': 1000010008, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Légkezelő L1 - Hatásos Telj. Max', 'sc': 1000010008, 'ch': 3, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Légkezelő L2 - Áram Max', 'sc': 1000010009, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Légkezelő L2 - Hatásos Telj. Max', 'sc': 1000010009, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Légkezelő L3 - Áram Max', 'sc': 1000010009, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus Légkezelő L3 - Hatásos Telj. Max', 'sc': 1000010009, 'ch': 5, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus PNMDEV szerver - Áram Max', 'sc': 1000010012, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'A'},
        {'pod': 'Modbus PNMDEV szerver - hatásos telj.', 'sc': 1000010012, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Rubicon vezérlő szekrény - Áram Max', 'sc': 1000010010, 'ch': 5, 'off': 0, 'mul': 1000,
         'unit': 'A'},
        {'pod': 'Modbus Rubicon vezérlő szekrény  - Hatásos telj.', 'sc': 1000010010, 'ch': 4, 'off': 0, 'mul': 10000,
         'unit': 'kWh'},
        {'pod': 'Modbus Szerverek előlapi hőmérséklete', 'sc': 1000010011, 'ch': 4, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Szerverek hátlapi hőmérséklet', 'sc': 1000010011, 'ch': 5, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Szerverszoba hőmérséklet padló', 'sc': 1000010011, 'ch': 7, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Modbus Szerverszoba hőmérséklet plafon', 'sc': 1000010011, 'ch': 6, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok'},
        {'pod': 'Rubin_Gáz', 'sc': 1015020426, 'ch': 7, 'off': 0, 'mul': 100, 'unit': 'm3'},
        {'pod': 'Rubin_Hőmennyiségmérő', 'sc': 1015020426, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'MWh'},
        {'pod': 'Rubin_HVAC_Fazis_1', 'sc': 1015020426, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_HVAC_Fazis_2', 'sc': 1015020426, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_HVAC_Fazis_3', 'sc': 1015020426, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Iroda_Fazis_1', 'sc': 1014100061, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Iroda_Fazis_2', 'sc': 1014100061, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Iroda_Fazis_3', 'sc': 1014100061, 'ch': 7, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Szerver_Fazis_1', 'sc': 1014100061, 'ch': 2, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Szerver_Fazis_2', 'sc': 1014100061, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_Szerver_Fazis_3', 'sc': 1014100061, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin_temp_irodaelore', 'sc': 1015020426, 'ch': 2, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok'},
        {'pod': 'Rubin_temp_irodavissza', 'sc': 1015020426, 'ch': 3, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok'},
        {'pod': 'Rubin_temp_kulső', 'sc': 1015020426, 'ch': 0, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok'},
        {'pod': 'Rubin Iroda TIP', 'sc': 1014100061, 'ch': 0, 'off': 0, 'mul': 250, 'unit': 'kWh'},
        {'pod': 'Rubin Iroda TIP meddő ', 'sc': 1014100061, 'ch': 1, 'off': 0, 'mul': 250, 'unit': 'kVArh'},
        {'pod': 'Rubin konyha 1 - Vízadagoló', 'sc': 2017111701, 'ch': 0, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin konyha 1 - Vízadagoló T', 'sc': 2017111701, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin konyha 2 - mosogató', 'sc': 2017111701, 'ch': 2, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin konyha 3 - kávéfőző', 'sc': 2017111701, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin konyha 4 - micró, vízforraló', 'sc': 2017111701, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh'},
        {'pod': 'Rubin konyha 5 - micró, teafőző', 'sc': 2017111701, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh'}
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
            port = DcSettings.DC_PORT
            r = requests.get(
                'http://localhost:{}/dc/client/lastmeasure?deviceid={}&channel={}'.format(port, sc, channel))
            dcDiAct = r.json()

            # Get timestamp
            dcTime = dcDiAct['output']['time']
            dcDateTime = datetime.strptime(dcTime, '%Y-%m-%dT%H:%M:%S')
            dcDateTimePrev = dcDateTime - timedelta(minutes=5)
            dcTimePrev = dcDateTimePrev.strftime('%Y-%m-%dT%H:%M:%S')

            # Get previous value
            r = requests.get(
                'http://localhost:{}/dc/client/measurevalue?deviceid={}&channel={}&time={}'.format(port, sc, channel,
                                                                                                   dcTimePrev))
            dcDiPrev = r.json()

            # Impulse value actual and previous
            impAct = dcDiAct['output']['value']
            impPrev = dcDiPrev['measureValue']['value']

            # Build up message
            dict_msg = {"pod_name": podDi['pod'],
                        "timestamp": dcTime,
                        "imp_count": impAct,
                        "imp_delta": impAct - impPrev}

            # Measurement value calculation based on unit
            if podDi['unit'] == DcSettings.MEA_UNIT_CURR:
                # Unit is current, value is (act-prev) / mul
                dict_msg["current"] = (impAct - impPrev) / podDi['mul']
            elif podDi['unit'] == DcSettings.MEA_UNIT_TEMP:
                # Unit is temperature, value is (act-prev) / mul - offs
                dict_msg["temperature"] = (impAct - impPrev) / podDi['mul'] - podDi['off']
            elif podDi['unit'] == DcSettings.MEA_UNIT_GAS:
                # Unit is m3, gas consumption a meter
                dict_msg["gas_cons"] = (impAct - impPrev) / podDi['mul']
                dict_msg["gas_meter"] = impAct / podDi['mul']
            elif podDi['unit'] == DcSettings.MEA_UNIT_HEAT:
                # Unit is MWh, Heat consumption
                dict_msg["heat_cons"] = (impAct - impPrev) / podDi['mul']
                dict_msg["heat_meter"] = impAct / podDi['mul']
            elif podDi['unit'] == DcSettings.MEA_UNIT_CONS:
                # Unit is kWh, Electrical consumption
                dict_msg["elec_cons"] = (impAct - impPrev) / podDi['mul']
                dict_msg["elec_meter"] = impAct / podDi['mul']
            elif podDi['unit'] == DcSettings.MEA_UNIT_REAC:
                # Unit is kWh, Electrical reactive consumption
                dict_msg["reac_cons"] = (impAct - impPrev) / podDi['mul']
                dict_msg["rec_meter"] = impAct / podDi['mul']
            else:
                # No unit is recogmised
                pass

            msg = json.dumps(dict_msg)
            print(msg)
            # self.mqttc.publish(DcSettings.MQTT_CHANNEL, msg)


if __name__ == '__main__':
    dmq = DcToMQ()
    dmq.produce()
    dmq.close()

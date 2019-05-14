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
    MQTT_HOST = "tick.rubin.hu"
    MQTT_PORT = 1883
    MQTT_KEEPALIVE_INTERVAL = 45
    MQTT_CHANNEL = "dc"
    MQTT_CHANNEL_VAL = "vdc"
    MQTT_CHANNEL_ROW = "rdc"
    DC_PORT = 2123
    POD_LIST = [
        {'pod': 'Modbus Brutál szerever - Áram Max', 'sc': 1000010012, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'A',
         "id": 1},
        {'pod': 'Modbus Brutál szerever - hatásos telj.', 'sc': 1000010012, 'ch': 4, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 2},
        {'pod': 'Modbus Csigabiga - hatásos telj.', 'sc': 1000010012, 'ch': 2, 'off': 0, 'mul': 10000, 'unit': 'kWh',
         "id": 3},
        {'pod': 'Modbus Csigabiga - Max Áram', 'sc': 1000010012, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'A', "id": 4},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 1 - hatásos telj.', 'sc': 1000010010, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 5},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 1 - Max Áram', 'sc': 1000010010, 'ch': 1, 'off': 0, 'mul': 1000,
         'unit': 'A', "id": 6},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 2 - Hatásos telj.', 'sc': 1000010010, 'ch': 2, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 7},
        {'pod': 'Modbus Légkezelő frekvenciaváltó 2 - Max Áram', 'sc': 1000010010, 'ch': 3, 'off': 0, 'mul': 1000,
         'unit': 'A', "id": 8},
        {'pod': 'Modbus Légkezelő hőcserélő bemenet hőmérséklet', 'sc': 1000010011, 'ch': 0, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 9},
        {'pod': 'Modbus Légkezelő hőcserélő kimenet hőmérséklet', 'sc': 1000010011, 'ch': 1, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 10},
        {'pod': 'Modbus Légkezelő iroda befújt levegő hőmérséklet', 'sc': 1000010011, 'ch': 2, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 11},
        {'pod': 'Modbus Légkezelő Iroda elszívott levegő hőmérs.', 'sc': 1000010011, 'ch': 3, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 12},
        {'pod': 'Modbus Légkezelő L1  - Áram Max', 'sc': 1000010008, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'A',
         "id": 13},
        {'pod': 'Modbus Légkezelő L1 - Hatásos Telj. Max', 'sc': 1000010008, 'ch': 3, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 14},
        {'pod': 'Modbus Légkezelő L2 - Áram Max', 'sc': 1000010009, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'A',
         "id": 15},
        {'pod': 'Modbus Légkezelő L2 - Hatásos Telj. Max', 'sc': 1000010009, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 16},
        {'pod': 'Modbus Légkezelő L3 - Áram Max', 'sc': 1000010009, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'A',
         "id": 17},
        {'pod': 'Modbus Légkezelő L3 - Hatásos Telj. Max', 'sc': 1000010009, 'ch': 5, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 18},
        {'pod': 'Modbus PNMDEV szerver - Áram Max', 'sc': 1000010012, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'A',
         "id": 19},
        {'pod': 'Modbus PNMDEV szerver - hatásos telj.', 'sc': 1000010012, 'ch': 0, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 20},
        {'pod': 'Modbus Rubicon vezérlő szekrény - Áram Max', 'sc': 1000010010, 'ch': 5, 'off': 0, 'mul': 1000,
         'unit': 'A', "id": 21},
        {'pod': 'Modbus Rubicon vezérlő szekrény  - Hatásos telj.', 'sc': 1000010010, 'ch': 4, 'off': 0, 'mul': 10000,
         'unit': 'kWh', "id": 22},
        {'pod': 'Modbus Szerverek előlapi hőmérséklete', 'sc': 1000010011, 'ch': 4, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 23},
        {'pod': 'Modbus Szerverek hátlapi hőmérséklet', 'sc': 1000010011, 'ch': 5, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 24},
        {'pod': 'Modbus Szerverszoba hőmérséklet padló', 'sc': 1000010011, 'ch': 7, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 25},
        {'pod': 'Modbus Szerverszoba hőmérséklet plafon', 'sc': 1000010011, 'ch': 6, 'off': 30, 'mul': 10,
         'unit': 'Celsius-fok', "id": 26},
        {'pod': 'Rubin_Gáz', 'sc': 1015020426, 'ch': 7, 'off': 0, 'mul': 100, 'unit': 'm3', "id": 27},
        {'pod': 'Rubin_Hőmennyiségmérő', 'sc': 1015020426, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'MWh', "id": 28},
        {'pod': 'Rubin_HVAC_Fazis_1', 'sc': 1015020426, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 29},
        {'pod': 'Rubin_HVAC_Fazis_2', 'sc': 1015020426, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 30},
        {'pod': 'Rubin_HVAC_Fazis_3', 'sc': 1015020426, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 31},
        {'pod': 'Rubin_Iroda_Fazis_1', 'sc': 1014100061, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 32},
        {'pod': 'Rubin_Iroda_Fazis_2', 'sc': 1014100061, 'ch': 6, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 33},
        {'pod': 'Rubin_Iroda_Fazis_3', 'sc': 1014100061, 'ch': 7, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 34},
        {'pod': 'Rubin_Szerver_Fazis_1', 'sc': 1014100061, 'ch': 2, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 35},
        {'pod': 'Rubin_Szerver_Fazis_2', 'sc': 1014100061, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 36},
        {'pod': 'Rubin_Szerver_Fazis_3', 'sc': 1014100061, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 37},
        {'pod': 'Rubin_temp_irodaelore', 'sc': 1015020426, 'ch': 2, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok',
         "id": 38},
        {'pod': 'Rubin_temp_irodavissza', 'sc': 1015020426, 'ch': 3, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok',
         "id": 39},
        {'pod': 'Rubin_temp_kulső', 'sc': 1015020426, 'ch': 0, 'off': 30, 'mul': 10, 'unit': 'Celsius-fok', "id": 40},
        {'pod': 'Rubin Iroda TIP', 'sc': 1014100061, 'ch': 0, 'off': 0, 'mul': 250, 'unit': 'kWh', "id": 41},
        {'pod': 'Rubin Iroda TIP meddő ', 'sc': 1014100061, 'ch': 1, 'off': 0, 'mul': 250, 'unit': 'kVArh', "id": 42},
        {'pod': 'Rubin konyha 1 - Vízadagoló', 'sc': 2017111701, 'ch': 0, 'off': 0, 'mul': 1000, 'unit': 'kWh',
         "id": 43},
        {'pod': 'Rubin konyha 1 - Vízadagoló T', 'sc': 2017111701, 'ch': 1, 'off': 0, 'mul': 1000, 'unit': 'kWh',
         "id": 44},
        {'pod': 'Rubin konyha 2 - mosogató', 'sc': 2017111701, 'ch': 2, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 45},
        {'pod': 'Rubin konyha 3 - kávéfőző', 'sc': 2017111701, 'ch': 3, 'off': 0, 'mul': 1000, 'unit': 'kWh', "id": 46},
        {'pod': 'Rubin konyha 4 - micró, vízforraló', 'sc': 2017111701, 'ch': 4, 'off': 0, 'mul': 1000, 'unit': 'kWh',
         "id": 47},
        {'pod': 'Rubin konyha 5 - micró, teafőző', 'sc': 2017111701, 'ch': 5, 'off': 0, 'mul': 1000, 'unit': 'kWh',
         "id": 48}
    ]
    MEA_UNIT_CURR = 'A'
    MEA_UNIT_CONS = 'kWh'
    MEA_UNIT_TEMP = 'Celsius-fok'
    MEA_UNIT_GAS = 'm3'
    MEA_UNIT_HEAT = 'MWh'
    MEA_UNIT_REAC = 'kVArh'


class DcToMQ:


    def produce(self):
        gdict_msg = {"pod_name": 'Rubin'}
        for podDi in DcSettings.POD_LIST:
            # Get DC
            sc = podDi['sc']
            channel = podDi['ch']
            port = DcSettings.DC_PORT
            url = 'http://localhost:{}/dc/client/lastmeasure?deviceid={}&channel={}'.format(port, sc, channel)
            # print(url)
            r = requests.get(url)
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
            # Build up single value message
            vdict_msg = {"pod_name": podDi['pod'],
                         "timestamp": dcTime,
                         "imp_count": impAct,
                         "imp_delta": impAct - impPrev}
            vdict2_msg = {"pod_name": podDi['pod'],
                          "timestamp": dcTime,
                          "imp_count": impAct,
                          "imp_delta": impAct - impPrev}
            # Build up single row message
            gdict_msg["timestamp"] = dcTime

            value, value2 = None, None
            # Measurement value calculation based on unit
            if podDi['unit'] == DcSettings.MEA_UNIT_CURR:
                # Unit is current, value is (act-prev) / mul
                value = (impAct - impPrev) / podDi['mul']
                dict_msg["current"] = value
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "current"
                gdict_msg['current_{}'.format(podDi["id"])] = value
            elif podDi['unit'] == DcSettings.MEA_UNIT_TEMP:
                # Unit is temperature, value is (act-prev) / mul - offs
                value = (impAct - impPrev) / podDi['mul'] - podDi['off']
                dict_msg["temperature"] = value
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "temperature"
                gdict_msg['temperature_{}'.format(podDi["id"])] = value
            elif podDi['unit'] == DcSettings.MEA_UNIT_GAS:
                # Unit is m3, gas consumption a meter
                value = (impAct - impPrev) / podDi['mul']
                value2 = impAct / podDi['mul']
                dict_msg["gas_cons"] = value
                dict_msg["gas_meter"] = value2
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "gas_cons"
                vdict2_msg['value'] = value2
                vdict2_msg['meas_typ'] = "gas_meter"
                gdict_msg['gas_cons_{}'.format(podDi["id"])] = value
                gdict_msg['gas_meter_{}'.format(podDi["id"])] = value2
            elif podDi['unit'] == DcSettings.MEA_UNIT_HEAT:
                # Unit is MWh, Heat consumption
                value = (impAct - impPrev) / podDi['mul']
                value2 = impAct / podDi['mul']
                dict_msg["heat_cons"] = value
                dict_msg["heat_meter"] = value2
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "heat_cons"
                vdict2_msg['value'] = value2
                vdict2_msg['meas_typ'] = "heat_meter"
                gdict_msg['heat_cons_{}'.format(podDi["id"])] = value
                gdict_msg['heat_meter_{}'.format(podDi["id"])] = value2
            elif podDi['unit'] == DcSettings.MEA_UNIT_CONS:
                # Unit is kWh, Electrical consumption
                value = (impAct - impPrev) / podDi['mul']
                value2 = impAct / podDi['mul']
                dict_msg["elec_cons"] = value
                dict_msg["elec_meter"] = value2
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "elec_cons"
                vdict2_msg['value'] = value2
                vdict2_msg['meas_typ'] = "elec_meter"
                gdict_msg['elec_cons_{}'.format(podDi["id"])] = value
                gdict_msg['elec_meter_{}'.format(podDi["id"])] = value2
            elif podDi['unit'] == DcSettings.MEA_UNIT_REAC:
                # Unit is kWh, Electrical reactive consumption
                value = (impAct - impPrev) / podDi['mul']
                value2 = impAct / podDi['mul']
                dict_msg["reac_cons"] = value
                dict_msg["rec_meter"] = value2
                vdict_msg['value'] = value
                vdict_msg['meas_typ'] = "reac_cons"
                vdict2_msg['value'] = value2
                vdict2_msg['meas_typ'] = "rec_meter"
                gdict_msg['reac_cons_{}'.format(podDi["id"])] = value
                gdict_msg['reac_meter_{}'.format(podDi["id"])] = value2
            else:
                # No unit is recogmised
                pass

            msg = json.dumps(dict_msg)
            print(msg)
            msgv = json.dumps(vdict_msg)
            print(msgv)
            mqttc = mqtt.Client()
            mqttc.connect(DcSettings.MQTT_HOST, DcSettings.MQTT_PORT, DcSettings.MQTT_KEEPALIVE_INTERVAL)
            mqttc.publish(DcSettings.MQTT_CHANNEL, msg)
            mqttc.publish(DcSettings.MQTT_CHANNEL_VAL, msgv)
            if value2 is not None:
                msgv = json.dumps(vdict2_msg)
                mqttc.publish(DcSettings.MQTT_CHANNEL_VAL, msgv)
            mqttc.disconnect()
        print("Send One Line Message...")
        msg = json.dumps(gdict_msg)
        print(msg)

        mqttc = mqtt.Client()
        mqttc.connect(DcSettings.MQTT_HOST, DcSettings.MQTT_PORT, DcSettings.MQTT_KEEPALIVE_INTERVAL)
        mqttc.publish(DcSettings.MQTT_CHANNEL_ROW, msg)
        mqttc.disconnect()

if __name__ == '__main__':
    dmq = DcToMQ()
    dmq.produce()
    #dmq.close()

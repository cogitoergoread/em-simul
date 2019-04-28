from unittest import TestCase
import lora


class TestDecoder(TestCase):
    def test_getSensStart_BattOnly(self):
        self.assertEqual({lora.SensorType.BATT: 0},
                         lora.Decoder.getSensStart(port=0))  # Battery van default

    def test_getSensStart_BattHumi(self):
        self.assertEqual({lora.SensorType.HUMI: 0, lora.SensorType.BATT: 8},
                         lora.Decoder.getSensStart(port=1 << lora.SensorType.HUMI))

    def test_getSensStart_All(self):
        self.assertEqual({lora.SensorType.PULSE: 0,
                          lora.SensorType.TEMP: 16,
                          lora.SensorType.HUMI: 24,
                          lora.SensorType.PRES: 32,
                          lora.SensorType.BATT: 40},
                         lora.Decoder.getSensStart(port=0b1111))

    def test_twos_complement(self):
        self.assertEqual(-2, lora.Decoder.twos_complement('FFFE', 16))
        self.assertEqual(32767, lora.Decoder.twos_complement('7FFF', 16))
        self.assertEqual(-32768, lora.Decoder.twos_complement('8000', 16))

    def test_hextoint(self):
        self.assertEqual(-2, lora.Decoder.hexToInt("FFFE", lora.DataType.INT16))
        self.assertEqual(65534, lora.Decoder.hexToInt("FFFE", lora.DataType.UINT16))
        self.assertEqual(1 * 256 ** 3 + 2 * 256 ** 2 + 3 * 256 + 4,
                         lora.Decoder.hexToInt('01020304', lora.DataType.UINT32))

    def test_d2di_batt(self):
        self.assertEqual({'battery': 5.11},
                         lora.Decoder.data_to_dict('01FF', 0))

    def test_d2di_humi_batt(self):
        self.assertEqual({'battery': 5.10,
                          'humidity': 0.999,
                          'hum_temp': 30.9},
                         lora.Decoder.data_to_dict('03E7013501FE',
                                                   1 << lora.SensorType.HUMI))
        self.assertEqual({'battery': 5.09},
                         lora.Decoder.data_to_dict('98767FFF01FD',
                                                   1 << lora.SensorType.HUMI))

    def test_d2di_pres_batt(self):
        self.assertEqual({'battery': 5.08,
                          'pressure': 1012,
                          'prs_temp': -12.3},
                         lora.Decoder.data_to_dict('03F4FF8501FC',
                                                   1 << lora.SensorType.PRES))
        self.assertEqual({'battery': 5.07},
                         lora.Decoder.data_to_dict('98767FFF01FB',
                                                   1 << lora.SensorType.PRES))

    def test_d2di_temp_batt(self):
        self.assertEqual({'battery': 5.06,
                          'temp_1': 28.9,
                          'temp_2': -5.6},
                         lora.Decoder.data_to_dict('0121FFC801FA',
                                                   1 << lora.SensorType.TEMP))
        self.assertEqual({'battery': 5.05},
                         lora.Decoder.data_to_dict('7FFF7FFF01F9',
                                                   1 << lora.SensorType.TEMP))
        self.assertEqual({'battery': 5.04,
                          'temp_1': 28.8},
                         lora.Decoder.data_to_dict('01207FFF01F8',
                                                   1 << lora.SensorType.TEMP))
        self.assertEqual({'battery': 5.03,
                          'temp_2': -5.7},
                         lora.Decoder.data_to_dict('7FFFFFC701F7',
                                                   1 << lora.SensorType.TEMP))

    def test_d2di_imp_batt(self):
        self.assertEqual({'battery': 5.02,
                          'pulse_1': 3487782347,
                          'pulse_2': 21399632},
                         lora.Decoder.data_to_dict('CFE355CB0146885001F6',
                                                   1 << lora.SensorType.PULSE))

    def test_d2di_ah_1(self):
        self.assertEqual({'battery': 3.37,
                          'hum_temp': 23.6,
                          'humidity': 0.363,
                          'pulse_1': 189,
                          'pulse_2': 295},
                         lora.Decoder.data_to_dict('000000bd00000127016b00ec0151',
                                                   5))

    def test_d2di_ah_2(self):
        self.assertEqual({'battery': 3.33,
                          'hum_temp': 23.9,
                          'humidity': 0.358,
                          'pulse_1': 13,
                          'pulse_2': 11,
                          'temp_1': 25.5},
                         lora.Decoder.data_to_dict('0000000d0000000b00ff7fff016600ef014d',
                                                   7))

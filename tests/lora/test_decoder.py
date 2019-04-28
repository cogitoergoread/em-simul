from unittest import TestCase
import lora


class TestDecoder(TestCase):
    def test_getSensStart_BattOnly(self):
        self.assertEqual({lora.SensorType.BATT: 0},
                         lora.Decoder.getSensStart(port=0))  # Battery van default

    def test_getSensStart_BattHumi(self):
        self.assertEqual({lora.SensorType.HUMI: 0, lora.SensorType.BATT: 4},
                         lora.Decoder.getSensStart(port=1 << lora.SensorType.HUMI))

    def test_getSensStart_All(self):
        self.assertEqual({lora.SensorType.PULSE: 0,
                          lora.SensorType.TEMP: 8,
                          lora.SensorType.HUMI: 12,
                          lora.SensorType.PRES: 16,
                          lora.SensorType.BATT: 20},
                         lora.Decoder.getSensStart(port=0b1111))

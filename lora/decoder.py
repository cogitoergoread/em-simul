"""
Rubin LORA szenzor pakolt adatformájának dekódolása.
Magyarázatok a RubinLoraPulseCounter_MuszakiAdatlap.docx doksiban, by Forati.
"""

from enum import unique, IntEnum


@unique
class SensorType(IntEnum):
    """
    Lora modul szenzor konstansok, bitszám szerint növő
    """
    PULSE = 0  # Impulzus szenzor, bytefolyam eleje, 2x 4 byte, 2 csatorna
    TEMP = 1  # Hőmérséklet szenzor, bytefolyam 2., 2x 2 byte
    HUMI = 2  # Páratartalom szenzor,  bytefolyam 3., 2x 2 byte
    PRES = 3  # Légynomás szenzor, bytefolyam 4., 2x 2 byte
    BATT = 4  # Elem feszültség, , bytefolyam 5., 1x 2 byte


class Consts:
    LENDTA = {SensorType.BATT: 2,
              SensorType.PULSE: 8,
              SensorType.TEMP: 4,
              SensorType.HUMI: 4,
              SensorType.PRES: 4}


class Decoder:
    @classmethod
    def getSensStart(cls, port: int):
        """
        Visszaadja, hogy adott port esetén van-e adat, és hol kezdődik
        :param port: Lora üzenetben definiált port
        :type port: int
        :return: {SensorType: kezdet}, ha van adat a szenzorhoz
        :rtype: dict
        """
        aktport = port + (1 << SensorType.BATT)  # Elem infó van minden esetben.
        retDi = dict()
        # Check port
        offset = 0
        for sens in SensorType:
            if aktport & (1 << sens):
                # Van port, vissza kell adni
                retDi[sens] = offset
                offset += Consts.LENDTA[sens]
        return retDi

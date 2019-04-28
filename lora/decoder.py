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


@unique
class DataType(IntEnum):
    """
    Lora modul Adattípusok
    """
    UINT32 = 0  # Unsigned int, 32 bit, bit 24-31, bit 16-23, bit 8-15, bit 0-7
    INT16 = 1  # Signed int, 16 bits, bit 8-15, bit 0-7
    UINT16 = 2  # Unsigned int, 16 bits, bit 8-15, bit 0-7


class Consts:
    LENDTA = {SensorType.BATT: 2,
              SensorType.PULSE: 8,
              SensorType.TEMP: 4,
              SensorType.HUMI: 4,
              SensorType.PRES: 4}
    SENSERR = "7FFF"


class Decoder:
    @classmethod
    def getSensStart(cls, port: int) -> dict:
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
                offset += 2 * Consts.LENDTA[sens]
        return retDi

    @classmethod
    def twos_complement(cls, hexstr: str, bits: int) -> int:
        """
        Hexa stringet konvertál előjelesre
        :param hexstr: Hexa string
        :type hexstr: str
        :param bits: Hány bit kell, 8 / 16
        :type bits: int
        :return: Konvertált érték
        :rtype: int
        """
        value = int(hexstr, 16)
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value

    @classmethod
    def hexToInt(cls, hexstr: str, dtasize: DataType) -> int:
        """
        Hexa kódolt stringből kibányássza a tatzalmazó adatot
        :param hexstr: feldolgozandó heya string
        :type hexstr: str
        :param dtasize: Milyen adatot adjon vissza
        :type dtasize: Lásd class DataType
        :return: int adat
        :rtype: int
        """
        if dtasize == DataType.INT16:
            return cls.twos_complement(hexstr, 16)
        else:
            return int(hexstr, 16)

    @classmethod
    def data_to_dict(cls, hexstr: str, port: int) -> dict:
        """
        Lora adat stringet dictionaryként adja vissza
        :param hexstr: Lora adatstring
        :type hexstr: str
        :param port: port azonosító
        :type port: int
        :return: Dictionary a becsomagolt adatokból
        :rtype: dict
        """
        retDi = dict()

        for sensType, offset in cls.getSensStart(port).items():
            if sensType == SensorType.BATT:
                # uint16, Elem feszültség értéke század voltban
                # pl: 3,36V = 336
                retDi['battery'] = float(cls.hexToInt(hexstr[offset:offset + 2 * Consts.LENDTA[sensType]],
                                                      DataType.UINT16)) / 100
            elif sensType == SensorType.HUMI:
                # Első 2 byte, uint16, Páratartalom értéke tized százalékban
                # pl: 68,4% = 684
                # Második 2 byte, int 16 Hőmérséklet tized fokban  pl: 22,3 = 223
                # Szenzor hiba esetén értéke: 0x7FFF
                strFirst = hexstr[offset:offset + 4]
                strSecond = hexstr[offset + 4:offset + 8]
                if not strSecond.upper() == Consts.SENSERR:
                    retDi['humidity'] = float(cls.hexToInt(strFirst, DataType.UINT16)) / 1000
                    retDi['hum_temp'] = float(cls.hexToInt(strSecond, DataType.INT16)) / 10
            elif sensType == SensorType.PRES:
                # Első 2 byte, uint16, Légnyomás értéke hPa-ban
                # pl: 1012hPa = 1012
                # Második 2 byte, int16, Hőmérséklet tized fokban  pl: 22,3 = 223
                # Szenzor hiba esetén értéke: 0x7FFF
                strFirst = hexstr[offset:offset + 4]
                strSecond = hexstr[offset + 4:offset + 8]
                if not strSecond.upper() == Consts.SENSERR:
                    retDi['pressure'] = cls.hexToInt(strFirst, DataType.UINT16)
                    retDi['prs_temp'] = float(cls.hexToInt(strSecond, DataType.INT16)) / 10
            elif sensType == SensorType.TEMP:
                # Első 2 byte, int16, 1-es vezetékes hőmérő hőmérséklet tized fokban pl: 23,7C = 237
                # Szenzor hiba esetén értéke: 0x7FFF
                # Második 2 byte, int16, 2-es vezetékes hőmérő hőmérséklet tized fokban pl: -5,6C = -56
                # Szenzor hiba esetén értéke: 0x7FFF
                strFirst = hexstr[offset:offset + 4]
                strSecond = hexstr[offset + 4:offset + 8]
                if not strFirst.upper() == Consts.SENSERR:
                    retDi['temp_1'] = float(cls.hexToInt(strFirst, DataType.INT16)) / 10
                if not strSecond.upper() == Consts.SENSERR:
                    retDi['temp_2'] = float(cls.hexToInt(strSecond, DataType.INT16)) / 10
            elif sensType == SensorType.PULSE:
                # Első 4 byte, uint32, 1-es impulzus bemenet számláló érték
                # Második 4 byte, uint32, 2-es impulzus bemenet számláló érték
                strFirst = hexstr[offset:offset + 8]
                strSecond = hexstr[offset + 8:offset + 16]
                retDi['pulse_1'] = cls.hexToInt(strFirst, DataType.UINT32)
                retDi['pulse_2'] = cls.hexToInt(strSecond, DataType.UINT32)
        return retDi

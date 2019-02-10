"""Statikus , Idő kezelés"""
import random


class Ido:
    HAJNAL = 0
    ORA = 3600
    PERC = 60
    EJFEL = 23 * ORA + 59 * PERC + 59

    @classmethod
    def getSec(cls, h: int = 0, m: int = 0, s: int = 0) -> int:
        """
        Visszaadja másodpercben az időt
        :param h: Óra
        :type h: int
        :param m: Perc
        :type m: int
        :param s: Másodperc
        :type s: int
        :return: Idő másodpercben
        :rtype: int
        """
        return h * cls.ORA + m * cls.PERC + s

    @classmethod
    def getRandSec(cls, h: int = 0, m: int = 0, s: int = 0, szoras: int = 0) -> int:
        """
        Véletlenszerű időt sorsol
        :param h: Óra
        :type h: int
        :param m: Perc
        :type m: int
        :param s: Másodperc
        :type s: int
        :param szoras: A szórés az adott időpont körül
        :type szoras:
        :return: Idő másodpercben
        :rtype: int
        """
        return int(max(cls.HAJNAL,
                       min(cls.EJFEL,
                           random.gauss(cls.getSec(h, m, s), szoras))))

    @classmethod
    def getRandIntLen(cls, len: int, szoras: int) -> int:
        """
        Véletlenszerű intervallum hosszt sorsol.
        :param len: Intervallum hossz
        :type len: int
        :param szoras: Intervallum hossz szórása
        :type szoras: int
        :return: Intervallum hossza
        :rtype: int
        """
        return int(max(0,
                       random.gauss(len, szoras)))

    @classmethod
    def getStr(cls, sec: int) -> str:
        """
        Visszaadja szépen formázott stringként
        :param sec: Idő másodpercben
        :type sec: int
        :return: Stringként prezentálva
        :rtype: str
        """
        hours = sec // 3600
        minutes = (sec - 3600 * hours) // 60
        seconds = sec - 3600 * hours - 60 * minutes
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


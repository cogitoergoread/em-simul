"""Szimulációban a fogyasztókat reprezentáló osztályok"""
import random
from typing import List, Tuple

from simul.SimLog import Event, EventType


class Fogyaszto:
    """
    Fogyasztó osztály, ebből származnak majd a konkrét fogyasztók, pl Fix
    """
    IdSeq = 0       # Innen tép ID-t

    id: int         # Fogyasztó azonosítója
    nev: str        # Fogyasztó neve
    telj: float     # Teljesítménye, mondjuk W
    szoras: float   # Teljesítmény szórása
    uzKezd: int     # Üzemidő kezdete, 0:00:00:00..(23*3600+59*60+59):23:59:59
    uzVeg: int      # Üzemidő vége, 0:00:00:00..(23*3600+59*60+59):23:59:59
    uzLi: List[Tuple[int,int]] # Lista az üzemelési időszakokról.

    def __init__(self, nev: str, telj: float, szoras: float, uzKezd: int, uzVeg: int):
        self.id = self.IdSeq
        self.IdSeq += 1
        self.nev = nev
        self.telj = telj
        self.szoras = szoras
        self.uzKezd = uzKezd
        self.uzVeg = uzVeg
        self.uzLi = [(uzKezd, uzVeg)]

    def getDta(self, timeStart: float, timeEnd: float) -> Tuple[float, List[Event]]:
        """
        Egy időszakra visszaadja az ahhoz tartozó fogyasztási és esmény adatokat
        :param timeStart: Időszak kezdete
        :type timeStart: float
        :param timeEnd: Időszak vége
        :type timeEnd: float
        :return: fogyasztás és esemény lista
        :rtype: Tuple[float, List[Event]]
        """
        fogyasztas = 0.0
        eventLi = list()
        for idokezd, idoveg in self.uzLi:
            if (idokezd < timeEnd) and (idoveg > timeStart):
                # Kell foglalkozni az időszakkal
                fogyasztas += (idoveg - idokezd) / 3600 * random.gauss(self.telj, self.szoras)
                if (idokezd >= timeStart) and (idokezd <= timeEnd):
                    eventLi.append(Event(idokezd, EventType.ESEMENY, self.id, 1))
                if (idoveg >= timeStart) and (idoveg <= timeEnd):
                    eventLi.append(Event(idoveg, EventType.ESEMENY, self.id, 0))
        return (fogyasztas, eventLi)
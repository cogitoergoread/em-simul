"""Szimulációban a fogyasztókat reprezentáló osztályok"""
import random
from typing import List, Tuple, Dict

import simul


class Fogyaszto:
    """
    Fogyasztó osztály, ebből származnak majd a konkrét fogyasztók, pl Fix
    """
    id: int         # Fogyasztó azonosítója
    nev: str        # Fogyasztó neve
    telj: float     # Teljesítménye, mondjuk W
    szoras: float   # Teljesítmény szórása
    uzKezd: int     # Üzemidő kezdete, 0:00:00:00..(23*3600+59*60+59):23:59:59
    uzVeg: int      # Üzemidő vége, 0:00:00:00..(23*3600+59*60+59):23:59:59
    uzLi: List[Tuple[int,int]] # Lista az üzemelési időszakokról.

    def __init__(self, id: int, nev: str, telj: float, szoras: float, uzKezd: int, uzVeg: int):
        self.id = id
        self.nev = nev
        self.telj = telj
        self.szoras = szoras
        self.uzKezd = uzKezd
        self.uzVeg = uzVeg
        self.uzLi = [(uzKezd, uzVeg)]

    def getDta(self, timeStart: int, timeEnd: int) -> Tuple[float, List[simul.Event]]:
        """
        Egy időszakra visszaadja az ahhoz tartozó fogyasztási és esmény adatokat
        :param timeStart: Időszak kezdete
        :type timeStart: int
        :param timeEnd: Időszak vége
        :type timeEnd: int
        :return: fogyasztás és esemény lista
        :rtype: Tuple[float, List[Event]]
        """
        fogyasztas = 0.0
        eventLi = list()
        for idokezd, idoveg in self.uzLi:
            if (idokezd < timeEnd) and (idoveg > timeStart):
                # Kell foglalkozni az időszakkal
                fogyasztas += ( min(idoveg, timeEnd) - max(idokezd, timeStart) + 1) / 3600\
                              * random.gauss(self.telj, self.szoras)
                if (idokezd >= timeStart) and (idokezd <= timeEnd):
                    eventLi.append(simul.Event(idokezd, simul.EventType.ESEMENY, self.id, 1))
                if (idoveg >= timeStart) and (idoveg <= timeEnd):
                    eventLi.append(simul.Event(idoveg, simul.EventType.ESEMENY, self.id, 0))
        return (fogyasztas, eventLi)

class Mero:
    """
    Fő vagy almérőt szimulál.
    Listája van az alá tartozó fogyasztókról
    """
    fogyasztok: List[int]
    id: int
    nev: str

    def __init__(self, id: int, nev: str, fogyasztok: List[int]):
        """
        Eltárolja az alá tartozó fogyasztó IDket.
        :param fogyasztok: Fogyasztó IDk
        :type fogyasztok: List[int]
        """
        self.id = id
        self.nev = nev
        self.fogyasztok = list()
        self.fogyasztok += fogyasztok

    def getAlhalozatiFOgyasztas(self, ossFogyasztas: Dict[int, float]) -> float:
        """
        Megadja az alhálózat fogyasztását
        :param ossFogyasztas: Minden fogyasztó fogyasztása
        :type ossFogyasztas: Dict[int, float]
        :return: Az alháló össz fogyasztása
        :rtype: float
        """
        ossz = 0.0
        for fogyaszto in self.fogyasztok:
            ossz += ossFogyasztas[fogyaszto]
        return ossz

class Halozat:
    """
    A hálózatban fogyasztók és mérők vannak.
    Egy intervllumra rögzít méréseket, és végigiterál a napon is.
    """
    fogyasztok: List[Fogyaszto]
    merok: List[Mero]
    recorder: simul.Record

    def __init__(self, recorder: simul.Record):
        self.fogyasztok = list()
        self.merok = list()
        self.recorder = recorder

    def getMeasDta(self, timeStart: int, timeEnd: int):
        """
        Egy intervallumra logba írja az adatokat
        :param timeStart: Időszak kezdete
        :type timeStart: int
        :param timeEnd: Időszak vége
        :type timeEnd: int
        """
        fogyasztasok = dict()
        for fogyaszto in self.fogyasztok:
            (value, evli) = fogyaszto.getDta(timeStart, timeEnd)
            for event in evli:
                self.recorder.log(event)
            fogyasztasok[fogyaszto.id] = value
        for mero in self.merok:
            self.recorder.log(simul.Event(timeEnd,
                                          simul.EventType.MERES,
                                          mero.id,
                                          mero.getAlhalozatiFOgyasztas(fogyasztasok)))

    def iterateOverDay(self, tickIntervel: int):
        """
        Végigmászik a napon, és megkérdez minden intervallumra értékeket
        :param tickIntervel: Ennyi másodpercenként mér.
        :type tickIntervel: int
        """
        startTime = 0
        lengthOfDay = 23*3600 + 59*60 + 59

        while startTime < lengthOfDay:
            self.getMeasDta(startTime,
                            min(lengthOfDay, startTime + tickIntervel -1))
            startTime += tickIntervel
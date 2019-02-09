"""Logolás"""
from enum import unique, IntEnum
from functools import total_ordering
from typing import List, Tuple
import json

@unique
class EventType(IntEnum):
    """
    Modul nevek
    """
    ESEMENY = 0
    MERES = 1

@total_ordering
class Event:
    timestamp: int      # Időpont másodpercben
    event: EventType    # Esemény típusa
    mid: int            # Mérő / fogyasztó azonosító
    value: float        # 0: kikapcs / 1 Bekapcs / mért érték

    def __init__(self, timestamp: int, event: EventType, mid: int, value: float):
        self.timestamp = timestamp
        self.event = event
        self.mid = mid
        self.value = value

    def __eq__(self, other):
        if type(other) is type(self):
            return self.timestamp == other.timestamp
        return False

    def __lt__(self, other):
        if type(other) is type(self):
            return self.timestamp < other.timestamp
        return NotImplemented


class EventEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, Event):
             return [obj.timestamp, obj.event, obj.mid, obj.value]
         # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)

class Record:
    """
    Esemény logokat tartalmaz
    """
    logok:  List[Tuple[int, EventType, int, float]]

    def __init__(self):
        self.logok = list()

    def log(self, event: Event):
        """
        Log eseményt elrak a listába
        """
        self.logok.append(event)

    def write(self, filename: str):
        self.logok.sort()
        with open(filename, 'w', encoding="utf-8") as file:
            json.dump(self.logok, file, cls=EventEncoder)
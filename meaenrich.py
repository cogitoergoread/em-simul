#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enrich JSON Measurement fields.
In: [timestamp: int, event: int, mid: int, value: float]
Out [Description]
"""

import sys
import json
import logging

# Set logging
logging.basicConfig(filename='example.log', level=logging.DEBUG)
fogydict = {1: 'Szerver Vitani', 2: 'Szerver Micimacko', 3: 'Szerver Brian', 4: 'Szerver Csigabiga',
            5: 'Szerver Csigabiga', 30: 'Konyha Hútő', 31: 'Konyha Mikro 1', 32: 'Konyha Mikro 2', 33: 'Konyha Mikro 3',
            34: 'Konyha lámpa', 40: 'Admin IldiPC', 41: 'Admin ZsaZsaPC', 42: 'Admin HajniPC', 43: 'Admin Radiátor'}
measdict = {1: 'Főmérő', 2: 'Szerver', 3: 'Adminn'}

if __name__ == '__main__':
    # Process the JSON from STDIN
    mearec = json.load(sys.stdin)
    logging.debug('Incoming')
    logging.debug(mearec)

    # Build up description string
    (timestamp, event, mid, value) = mearec[0], mearec[1], mearec[2], mearec[3]
    descr = ""
    if event == 0:
        descr = fogydict[mid]
        if value == 1:
            descr += " bekapcsolás"
        else:
            descr += " kikapcsolás"
    else:
        descr = "{} mérés {} W".format(measdict[mid], value)
    print(descr)

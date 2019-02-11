#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enrich JSON Measurement fields.
In: [timestamp: int, event: int, mid: int, value: float]
Out [Description]
"""

import sys
import json
import simul
import logging

# Set logging
logging.basicConfig(filename='example.log', level=logging.DEBUG)
fogydict = {1: 'Szerver Vitani', 2: 'Szerver Micimacko', 3: 'Szerver Brian', 4: 'Szerver Csigabiga',
            5: 'Szerver Csigabiga', 30: 'Konyha Hútő', 31: 'Konyha Mikro 1', 32: 'Konyha Mikro 2', 33: 'Konyha Mikro 3',
            34: 'Konyha lámpa', 40: 'Admin IldiPC', 41: 'Admin ZsaZsaPC', 42: 'Admin HajniPC', 43: 'Admin Radiátor'}
measdict = {1: 'Főmérő', 2: 'Szerver', 3: 'Adminn'}

if __name__ == '__main__':
    # Process the JSON from STDIN
    data_rec = json.load(sys.stdin)
    logging.debug('Incoming')
    logging.debug(data_rec)

    # Build up description string
    print(data_rec)

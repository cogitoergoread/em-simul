from unittest import TestCase
import simul
from random import seed

class TestIdo(TestCase):
    def setUp(self):
        seed(314)

    def test_getSec(self):
        self.assertEqual(23 * 3600+ 59 * 60 + 59, simul.Ido.getSec(23, 59, 59))

    def test_getRandSec(self):
        self.assertEqual(43989, simul.Ido.getRandSec(12, 12, 12, 360))

    def test_getRandIntLen(self):
        self.assertEqual(3657, simul.Ido.getRandIntLen(3600, 360))

    def test_getStr(self):
        self.assertEqual("01:02:03", simul.Ido.getStr(simul.Ido.getSec(1,2,3)))
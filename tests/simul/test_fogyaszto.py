from random import seed
from unittest import TestCase
import simul

class TestFogyaszto(TestCase):
    def setUp(self):
        self.f = simul.Fogyaszto(1, "Lámpa", 100, 0, 0, 23*3600 + 59*60 + 59)

    def test_getDta_egesznap(self):
        (fogyasztas, evlist) = self.f.getDta(0, 23*3600 + 59*60 + 59)
        self.assertEqual(100 * 24, fogyasztas)
        self.assertEqual(2, len(evlist))
        self.assertTrue(simul.Event(0, simul.EventType.ESEMENY, 1, 1.0).eq(evlist[0]))
        self.assertTrue(simul.Event(23*3600 + 59*60 + 59, simul.EventType.ESEMENY, 1, 0.0).eq(evlist[1]))

    def test_getDta_egyora_bovebb(self):
        self.f.uzLi.clear()
        self.f.uzLi.append((1*3600, 1*3600+59*60+59))                   # 01:00:00 - 01:59:59
        (fogyasztas, evlist) = self.f.getDta(0, 2*3600 + 59*60 + 59)    # 00:00:00 - 02:59:59
        self.assertEqual(100 * 1, fogyasztas)
        self.assertEqual(2, len(evlist))
        self.assertTrue(simul.Event(1*3600, simul.EventType.ESEMENY, 1, 1.0).eq(evlist[0]))
        self.assertTrue(simul.Event(1*3600 + 59*60 + 59, simul.EventType.ESEMENY, 1, 0.0).eq(evlist[1]))

    def test_getDta_ketora_szukebb(self):
        self.f.uzLi.clear()
        self.f.uzLi.append((1*3600-1, 2*3600+59*60+59))                   # 00:59:59 - 02:59:59
        (fogyasztas, evlist) = self.f.getDta(1*3600, 1*3600 + 59*60 + 59)    # 01:00:00 - 01:59:59
        self.assertEqual(100 * 1, fogyasztas)
        self.assertEqual(0, len(evlist))

    def test_getDta_ketszeregyora_bovebb(self):
        self.f.uzLi.clear()
        self.f.uzLi.append((1*3600, 1*3600+59*60+59))                   # 01:00:00 - 01:59:59
        self.f.uzLi.append((3*3600, 3*3600+59*60+59))                   # 03:00:00 - 03:59:59
        (fogyasztas, evlist) = self.f.getDta(0, 4*3600 + 59*60 + 59)    # 00:00:00 - 04:59:59
        self.assertEqual(100 * 2, fogyasztas)
        self.assertEqual(4, len(evlist))
        self.assertTrue(simul.Event(1*3600, simul.EventType.ESEMENY, 1, 1.0).eq(evlist[0]))
        self.assertTrue(simul.Event(1*3600 + 59*60 + 59, simul.EventType.ESEMENY, 1, 0.0).eq( evlist[1]))
        self.assertTrue(simul.Event(3*3600, simul.EventType.ESEMENY, 1, 1.0).eq( evlist[2]))
        self.assertTrue(simul.Event(3*3600 + 59*60 + 59, simul.EventType.ESEMENY, 1, 0.0).eq( evlist[3]))

    def test_getDta_ketszeregyora_metszet(self):
        self.f.uzLi.clear()
        self.f.uzLi.append((30*60, 1*3600+29*60+59))                   # 00:30:00 - 01:29:59
        self.f.uzLi.append((2*3600+30*60, 3*3600+59*60+59))                   # 02:30:00 - 03:59:59
        (fogyasztas, evlist) = self.f.getDta(1*3600, 2*3600 + 59*60 + 59)    # 01:00:00 - 02:59:59
        self.assertEqual(100 * 1, fogyasztas)
        self.assertEqual(2, len(evlist))
        self.assertTrue(simul.Event(1*3600 + 29*60 + 59, simul.EventType.ESEMENY, 1, 0.0).eq( evlist[0]))
        self.assertTrue(simul.Event(2*3600+30*60, simul.EventType.ESEMENY, 1, 1.0).eq( evlist[1]))


class TesztCiklikusFogyaszto(TestCase):
    def test_init(self):
        seed(314)
        f = simul.CiklikusFogyaszto(3, "Radiátor", 3000, 100,
                                    simul.Ido.getSec(10, 0, 0), simul.Ido.getSec(10, 14, 59),
                                    2 * 60, 60,
                                    3 * 60, 60)
        self.assertEqual(3, len(f.uzLi))
        self.assertEqual([(36000, 36129), (36338, 36542), (36725, 36849)],
                         f.uzLi)


class TestSpotFogyaszto(TestCase):
    def test_init(self):
        seed(314)
        f = simul.SpotFogyaszto(4, "WC lámpa", 50, 5,
                                simul.Ido.getSec(10, 0, 0), simul.Ido.getSec(15, 59, 59),
                                2 * 60, 3 * 60 / 2, 3)
        self.assertEqual(3, len(f.uzLi))
        self.assertEqual([(42436, 66), (56658, 135), (56582, 96)], f.uzLi)

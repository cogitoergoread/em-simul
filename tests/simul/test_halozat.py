from unittest import TestCase
import simul

class TestHalozat(TestCase):
    def setUp(self):
        self.fo1 = simul.Fogyaszto(1, "Szerver", 1000, 0, simul.Ido.HAJNAL, simul.Ido.EJFEL)
        self.fo2 = simul.Fogyaszto(2, "PC", 200, 0, simul.Ido.getSec(10), simul.Ido.getSec(13, 59, 59))
        self.m1 = simul.Mero(1, "Főmérő", [1, 2])
        self.m2 = simul.Mero(2, "Almérő", [2])
        self.rec = simul.Record()
        self.halo = simul.Halozat(self.rec)
        self.halo.merok += [self.m1, self.m2]
        self.halo.fogyasztok += [self.fo1, self.fo2]

    def test_iterateOverDay(self):
        self.halo.iterateOverDay(tickIntervel=simul.Ido.getSec(12))
        print(self.rec.logok)
        self.assertEqual(8,len(self.rec.logok))

        self.assertTrue(simul.Event(0, simul.EventType.ESEMENY, 1, 1).eq( self.rec.logok[0])) # Szerver be
        self.assertTrue(simul.Event(36000, simul.EventType.ESEMENY, 2, 1).eq( self.rec.logok[1])) # PC be
        self.assertTrue(simul.Event(simul.Ido.getSec(11,59,59),
                                    simul.EventType.MERES, 1, 12400).eq( self.rec.logok[2])) # Főmérő
        self.assertTrue(simul.Event(simul.Ido.getSec(11,59,59),
                                    simul.EventType.MERES, 2, 400).eq( self.rec.logok[3])) # Almérő
        self.assertTrue(simul.Event(simul.Ido.getSec(23,59,59),
                                    simul.EventType.ESEMENY, 1, 0).eq( self.rec.logok[4])) # Szerver ki
        self.assertTrue(simul.Event(simul.Ido.getSec(13,59,59),
                                    simul.EventType.ESEMENY, 2, 0).eq( self.rec.logok[5])) # PC ki
        self.assertTrue(simul.Event(simul.Ido.getSec(23,59,59),
                                    simul.EventType.MERES, 1, 12400).eq( self.rec.logok[6])) # Főmérő
        self.assertTrue(simul.Event(simul.Ido.getSec(23,59,59),
                                    simul.EventType.MERES, 2, 400).eq( self.rec.logok[7])) # Almérő
        self.rec.write("F:/tmp/log_s.json")

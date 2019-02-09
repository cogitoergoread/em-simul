import json
from unittest import TestCase
import simul

class TestEvent(TestCase):
    def setUp(self):
        self.e1 = simul.Event(1,0,0,0.0)
        self.e2 = simul.Event(2,1,1,1.0)

    def test_eq(self):
        self.assertTrue(self.e1 == self.e1)
        self.assertTrue(self.e1 == simul.Event(1,1,1,1.0))
        self.assertFalse(self.e1 == self.e2)

    def test_eqeq(self):
        self.assertTrue(self.e1.eq(self.e1))
        self.assertFalse(self.e1.eq(simul.Event(1,1,1,1.0)))
        self.assertTrue(self.e1.eq(simul.Event(1,0,0,0.0)))
        self.assertFalse(self.e1.eq(self.e2))

    def test_gt(self):
        self.assertFalse(self.e1 < self.e1)
        self.assertTrue(self.e1 < self.e2)

class TestRecord(TestCase):
    def setUp(self):
        self.e1 = simul.Event(1,0,0,0.0)
        self.e2 = simul.Event(2,1,1,1.0)
        self.r = simul.Record()

    def test_log(self):
        self.r.log(self.e1)
        self.assertEqual(1, len(self.r.logok))
        self.assertEqual(self.e1, self.r.logok[0])

    def test_write(self):
        self.r.log(self.e2)
        self.r.log(self.e1)
        fname = "F:/tmp/log_s.json"
        self.r.write(fname)
        loaded = None
        with open(fname, 'r', encoding="utf-8") as file:
            loaded = json.load(file)
        (timestamp, event, mid, value) = loaded[0]
        self.assertEqual(1, timestamp)
        self.assertEqual(0, event)
        self.assertEqual(0, mid)
        self.assertEqual(0.0, value)
from unittest import TestCase
from model import DayStructure


class DayTest(TestCase):
    def test_get_times(self):
        day = DayStructure()
        data = day.get_times()
        for i in data:
            self.assertEqual(i[2], 4)  # All should be undefined

    def test_get_time(self):
        day = DayStructure()
        self.assertEqual(day.get_time(0), (8, 10, 4))

    def test_set_time(self):
        day = DayStructure()
        day.set_time(0, 3)
        self.assertEqual(day.get_time(0)[2], 3)
        self.assertRaises(AssertionError, day.get_time, index=8)

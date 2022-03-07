from unittest import TestCase
from model import WeekStructure, DayStructure


class WeekTest(TestCase):
    def test_get_day(self):
        week = WeekStructure()
        self.assertEqual(week.get_day(0).get_time(0)[2], 4)
        self.assertRaises(AssertionError, week.get_day, 8)
        self.assertRaises(AssertionError, week.get_day, -1)

    def test_match(self):
        week1 = WeekStructure()
        week2 = WeekStructure()
        self.assertTrue(week1.matches(week2))
        self.assertTrue(week2.matches(week1))
        my_day = DayStructure(start=9, end=21, step=2)
        week3 = WeekStructure(data=[my_day]*7)
        self.assertFalse(week1.matches(week3))
        self.assertFalse(week3.matches(week1))
        # There are many more tests to make sure this "match" method work!

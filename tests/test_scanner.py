from unittest import TestCase
from model import StudentManager, Scanner


class ScannerTest(TestCase):
    def test_simple_scan(self):
        man = StudentManager()
        man.add_student("Esmail", 21)
        scan = Scanner()
        scan.add_student_manager(man)
        self.assertEqual(scan.get_student(21).name, "Esmail")
        scan.add_student("Ali", 22)
        self.assertEqual(scan.get_student(22).name, "Ali")
        self.assertEqual(scan.get_student(21).name, "Esmail")
        scan2 = Scanner()
        scan2.add_student("Esmail", 23)
        self.assertEqual(scan2.get_student(23).name, "Esmail")
        esmail = scan2.get_student(23)
        esmail.week.get_day(0).set_time(1, 0)
        esmail.week.get_day(2).set_time(3, 0)
        scan2.add_student_manager(scan._manager)
        self.assertEqual(scan2.get_student(22).name, "Ali")
        plot = scan2.plot_week([0], [3])
        self.assertFalse(plot.is_on(0, 1))
        self.assertFalse(plot.is_on(0, 1))  # just in case!
        self.assertFalse(plot.is_on(2, 3))
        ali = scan2.get_student(22)
        ali.week.get_day(1).set_time(2, 0)
        plot2 = scan2.plot_week([0], [3])
        self.assertFalse(plot2.is_on(1, 2))
        self.assertFalse(plot2.is_on(0, 1))
        self.assertFalse(plot2.is_on(2, 3))
        ali.set_importance(0)
        plot3 = scan2.plot_week([0], [3])
        self.assertTrue(plot3.is_on(1, 2))
        self.assertFalse(plot3.is_on(0, 1))

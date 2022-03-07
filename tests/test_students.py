from unittest import TestCase
from model import Student, StudentManager


class StudentTest(TestCase):
    def test_set_importance(self):
        stu = Student("Esmail", 973112255)
        self.assertEqual(stu.importance, 1)
        stu.set_importance(2)
        self.assertEqual(stu.importance, 2)
        self.assertRaises(AssertionError, stu.set_importance, new=5)


class StudentManagerTest(TestCase):
    def test_add_find(self):
        man = StudentManager()
        man.add_student("Esmail", 973112255)
        self.assertEqual(man.get_student(973112255).name, "Esmail")
        self.assertIsNone(man.get_student(5))
        a = 0
        for stu in man.get_students():
            self.assertEqual(stu.name, "Esmail")
            a += 1
        self.assertEqual(a, 1)  # this for should only iterate once, since there is only one element

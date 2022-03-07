from unittest import TestCase, TestLoader, TextTestRunner, main
from model import StudentManager, Export, Import
from os import remove


class ExportImportTest(TestCase):
    def test_export_import(self):
        self.man = man = StudentManager()
        man.add_student("Esmail", 973112255)
        Export('temp.pkl', man)
        Import('temp.pkl', self.received)
        # Fixme: It's possible that tearDown method called before Import finishes,
        #   it's running in another thread. use .join() might solve it.

    def received(self, man2):
        self.assertEqual(self.man.get_student(973112255).name,
                         man2.get_student(973112255).name)

    def tearDown(self) -> None:
        remove('temp.pkl')


# def run_tests():
#     loader = TestLoader()
#     suite = loader.discover('')
#     runner = TextTestRunner()
#     runner.run(suite)


# if __name__ == '__main__':
#     run_tests()

from model import Core
from qt_gui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication


def run(core: Core):
    app = QApplication([])
    win = MainWindow(core)
    win.show()
    return app.exec()


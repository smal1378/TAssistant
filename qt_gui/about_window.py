from PyQt5.QtCore import pyqtSignal

from qt_gui.designer.about import Ui_About
from PyQt5.QtWidgets import QWidget, QMessageBox, QDialog


class About(QDialog, Ui_About):
    set_text = pyqtSignal("QString")

    def __init__(self, master, text: str):
        super(About, self).__init__(master)
        self.setupUi(self)
        # noinspection PyUnresolvedReferences
        self.set_text.emit(text)


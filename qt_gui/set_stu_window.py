from typing import Union

from PyQt5.QtCore import pyqtSignal

from qt_gui.designer.set_student import Ui_New_Stu
from PyQt5.QtWidgets import QDialog


class SetStudent(QDialog, Ui_New_Stu):
    set_id = pyqtSignal("QString")
    set_name = pyqtSignal("QString")
    set_github = pyqtSignal("QString")
    entered = pyqtSignal("QString", "QString", "QString")

    def __init__(self, master, name: str = "", id_: Union[str, int] = "", github: str = ""):
        super(SetStudent, self).__init__(master)
        self.setupUi(self)
        if name:
            # noinspection PyUnresolvedReferences
            self.set_name.emit(name)
        if id_:
            # noinspection PyUnresolvedReferences
            self.set_id.emit(id_)
        if github:
            # noinspection PyUnresolvedReferences
            self.set_github.emit(github)
        self.label_error.setVisible(False)

    def button_ok(self):
        # noinspection PyUnresolvedReferences
        self.entered.emit(self.lineEdit.text(), self.lineEdit_2.text(), self.lineEdit_3.text())

    def show_error(self, text: str):
        self.label_error.setVisible(True)
        self.label_error.setText(text)

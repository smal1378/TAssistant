from typing import Callable, Optional

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QCheckBox


class AskToSave(QDialog):
    def __init__(self, master, callback_yes: Callable, callback_no: Callable):
        super(AskToSave, self).__init__(master)
        f = self.font()
        f.setPointSize(14)
        self.setFont(f)
        lay = QVBoxLayout()
        ver = QHBoxLayout()
        lay.addWidget(QLabel("There Were Some Changes Detected During Your Sessions<br>"
                             "Save Changes Before Exit?"))
        b = QPushButton("Yes")
        b.clicked.connect(lambda: callback_yes())
        # b.setShortcut("Enter")
        ver.addWidget(b)
        b = QPushButton("Discard")
        b.clicked.connect(lambda: callback_no())
        ver.addWidget(b)
        b = QPushButton("Cancel")
        b.setShortcut("Esc")
        b.clicked.connect(self.close)
        ver.addWidget(b)
        lay.addLayout(ver)
        self.setLayout(lay)


class ErrorMessage(QMessageBox):
    def __init__(self, master, message: str):
        super(ErrorMessage, self).__init__(master)
        self.setText(message)
        self.setWindowTitle("Error")


class LineGet(QDialog):
    def __init__(self, master, message: str, validator: Callable[[str], bool] = None):
        super(LineGet, self).__init__(master)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.validator = validator
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        lay = QVBoxLayout()
        self.setLayout(lay)
        self.line = QLineEdit()
        self.line.setPlaceholderText(message)
        lay.addWidget(self.line)
        self.data = ""
        self._checkboxes = {}  # name: bool

    def set_checkbox(self, name: str, message: str, default: bool = False):
        self._checkboxes[name] = 2 if default else 0
        check = QCheckBox(message)
        check.setCheckState(2 if default else 0)
        check.stateChanged.connect(lambda x, y=name: self._checkboxes.__setitem__(y, x))
        lay = self.layout()
        lay.addWidget(check)

    def get_checkbox(self, name: str):
        return True if self._checkboxes[name] == 2 else False

    def get(self):
        self.exec()
        return self.data

    def event(self, a0: QtCore.QEvent) -> bool:
        super(LineGet, self).event(a0)
        if a0.type() == a0.KeyPress:
            if a0.key() == QtCore.Qt.Key_Return:
                if self.validator(self.line.text()):
                    self.data = self.line.text()
                    self.close()
                else:
                    self.line.selectAll()
            elif a0.key() == QtCore.Qt.Key_Escape:
                self.close()
        return True


class AskYesNo(QDialog):
    def __init__(self, parent, message: str, on_yes: Callable = None, on_no: Callable = None):
        super(AskYesNo, self).__init__(parent)
        self.setWindowTitle("You Sure?")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.res = None
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        lay = QVBoxLayout()
        self.setLayout(lay)
        hor = QHBoxLayout()
        lab = QLabel(message)
        lab.setWordWrap(True)
        lab.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lab)
        lay.addLayout(hor)
        but = QPushButton("Yes")
        but.clicked.connect(lambda: on_yes() if on_yes else None)
        but.clicked.connect(lambda: self.__setattr__('res', True))
        but.clicked.connect(self.close)
        hor.addWidget(but)
        but2 = QPushButton("No")
        but2.clicked.connect(lambda: on_no() if on_no else None)
        but2.clicked.connect(lambda: self.__setattr__('res', False))
        but2.clicked.connect(self.close)
        hor.addWidget(but2)
        but.setFocus()

    def is_yes(self) -> Optional[bool]:
        if self.res is None:
            self.exec()
        return self.res


import os.path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListView, QTreeView, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QFileDialog

from model import StudentManager
from qt_gui.student_window import StudentView


class StudentsList(QDialog):
    on_need_to_save = pyqtSignal()

    def __init__(self, parent, manager: StudentManager):
        super(StudentsList, self).__init__(parent)
        self.manager = manager
        self.setWindowTitle(f"Students Of {manager.name}")
        self.setMinimumWidth(500)
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        lay = QVBoxLayout()
        self.setLayout(lay)
        wid = QTreeWidget()
        lay.addWidget(wid)
        wid.setColumnCount(3)
        wid.setHeaderLabels(["Name", "ID", "Github"])
        wid.setColumnWidth(0, 200)
        wid.setColumnWidth(1, 100)
        wid.setColumnWidth(2, 180)
        for student in manager.get_students():
            wid.addTopLevelItem(QTreeWidgetItem([student.name, str(student.id), student.github]))
        wid.itemDoubleClicked.connect(self.double_click)
        btn = QPushButton("Export Github Ids")
        btn.clicked.connect(self.export_btn)
        lay.addWidget(btn)

    def double_click(self, e: QTreeWidgetItem):
        stu = self.manager.get_student(int(e.text(1)))
        view = StudentView(self, stu, True)
        # noinspection PyUnresolvedReferences
        view.on_need_to_save.connect(lambda: self.on_need_to_save.emit())
        view.show()

    def export_btn(self):
        dialog = QFileDialog(self, "Save Export File")
        filename = dialog.getSaveFileName(filter="Text File(*.txt)")[0]
        if filename:
            with open(filename, "w") as file:
                for student in self.manager.get_students():
                    if student.github:
                        file.write(student.github)
                        file.write("\n")

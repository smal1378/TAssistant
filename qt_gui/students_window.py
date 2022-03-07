from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListView, QTreeView, QTreeWidget, QTreeWidgetItem

from model import StudentManager
from qt_gui.student_window import StudentView


class StudentsList(QDialog):
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

    def double_click(self, e):
        e: QTreeWidgetItem
        stu = self.manager.get_student(int(e.text(1)))
        StudentView(self, stu, True).show()


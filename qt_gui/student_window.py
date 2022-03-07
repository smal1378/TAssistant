from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QVBoxLayout, QGridLayout, QSizePolicy, QComboBox, QHBoxLayout, \
    QFrame

from model import Student, DayStructure


class Cell(QWidget):
    class _StateTraverser:
        def __init__(self, time_states, initial=None):
            self.states = list(time_states.keys())
            if initial is not None:
                self.index = self.states.index(initial)
            else:
                self.index = -1

        def next(self):
            self.index = (self.index + 1) % len(self.states)
            return self.states[self.index]

    def __init__(self, day: DayStructure, index: int, edit: bool = False):
        super(Cell, self).__init__()
        self.day = day
        self.edit = edit
        self.index = index
        self.setMinimumSize(125, 60)
        self.state = day.get_time(index)[2]
        self.state_traverser = Cell._StateTraverser(day.time_states, self.state)
        lay = QVBoxLayout()
        self.setLayout(lay)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wid = QLabel(day.time_states[self.state][0])
        self.wid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wid.setAlignment(QtCore.Qt.AlignCenter)
        self.wid.setStyleSheet(f"background: {day.time_state_colors[self.state]};"
                               f"font-size: 12pt;")
        lay.addWidget(self.wid)
        self.setFocusPolicy(QtCore.Qt.TabFocus | QtCore.Qt.ClickFocus)

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.MouseButtonRelease == a0.type():
            self.change_state()
            return True
        elif a0.KeyPress == a0.type() and a0.key() == QtCore.Qt.Key_Return:
            self.change_state()
            return True
        return False

    def change_state(self):
        if not self.edit:
            return
        self.parent().parent().need_to_save = True
        self.state = self.state_traverser.next()
        self.wid.setText(self.day.time_states[self.state][0])
        self.wid.setStyleSheet(f"background: {self.day.time_state_colors[self.state]};"
                               f"font-size: 12pt;")
        self.day.set_time(self.index, self.state)


class StudentView(QDialog):
    def __init__(self, parent, student: Student, edit: bool = False):
        super(StudentView, self).__init__(parent)
        self.student = student
        self.edit = edit
        self.setWindowTitle("Student View")
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        v_lay = QVBoxLayout()
        lay = QGridLayout()
        lay.setContentsMargins(15, 15, 15, 15)
        v_lay.addWidget(QLabel(f"{student.name} - {student.id} - {student.github}"), 0,
                        QtCore.Qt.AlignCenter)
        importance_lay = QHBoxLayout()
        comb = QComboBox()
        importance_lay.addWidget(QLabel("How Much Student Wants To Join The Meetings? "), 0)
        importance_lay.addWidget(comb, 1)
        v_lay.addLayout(importance_lay)
        v_lay.addLayout(lay)
        self.setLayout(v_lay)
        counter = 1
        for start, end, _ in student.week.get_day(0).get_times():
            lay.addWidget(QLabel(f"{start}-{end}"), counter, 0, QtCore.Qt.AlignCenter)
            counter += 1
        counter = 1
        for i in range(7):
            lay.addWidget(QLabel(f"{student.week.day_names[i][0]}"), 0, counter,
                          QtCore.Qt.AlignCenter)
            counter += 1

        counter1 = 1
        for day in student.week:
            counter2 = 1
            for _, _, state in day.get_times():
                lay.addWidget(Cell(day, counter2-1, edit), counter2, counter1)
                counter2 += 1
            counter1 += 1

        key_to_index = {}
        index = 0
        for key in student.importance_states:
            key_to_index[key] = index
            comb.addItem(student.importance_states[key][0], key)
            index += 1
        comb.setCurrentIndex(key_to_index[student.importance])
        comb.currentIndexChanged.connect(lambda e: (student.set_importance(comb.itemData(e)),
                                                    self.parent().__setattr__('need_to_save', True)))


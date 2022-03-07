from typing import Dict

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QGridLayout, QPushButton, \
    QFileDialog

from model import PlotResult, WeekStructure


class Cell(QWidget):
    def __init__(self, day: int, index: int, plot: PlotResult):
        super(Cell, self).__init__()
        data = plot.get(day, index)
        tool = f""
        maxi = 0
        value = 0
        for key in data:
            if data[key] >= value:
                value = data[key]
                maxi = key
            tool += f"{plot.time_states[key][0]}: {data[key]}\n"

        self.setStyleSheet(f"background-color: {'#afa' if plot.is_on(day, index) else '#faa'};"
                           f"font-size: 12pt;")
        lay = QVBoxLayout()
        self.setLayout(lay)
        lay.addWidget(QLabel(f"{plot.time_states[maxi][0]}: {value}"))
        self.setToolTip(tool)


class Plot(QDialog):
    def __init__(self, parent, plot: PlotResult):
        super(Plot, self).__init__(parent)
        self.plot = plot
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        lay1 = QHBoxLayout()
        lay1.addWidget(QLabel(f"ID: {plot.id}"))
        note = QLineEdit(plot.note)
        note.textChanged.connect(lambda: plot.__setattr__('note', note.text()))
        lay1.addWidget(note)
        lay = QVBoxLayout()
        self.setLayout(lay)
        lay.addLayout(lay1)
        grid = QGridLayout()
        lay.addLayout(grid)
        but = QPushButton("Export")
        but.clicked.connect(self.export)
        lay.addWidget(but)
        but2 = QPushButton("Add To Scan Results")
        but2.setEnabled(False)
        lay.addWidget(but2)
        grid.setContentsMargins(15, 15, 15, 15)
        for day in range(7):
            grid.addWidget(QLabel(WeekStructure.day_names[day][0]), 0, day + 1, QtCore.Qt.AlignCenter)

        for index, (start, end) in enumerate(plot.daily_time_data):
            grid.addWidget(QLabel(f"{start}-{end}"), index + 1, 0)

        for day in range(7):
            for index in range(len(plot.daily_time_data)):
                grid.addWidget(Cell(day, index, plot), index+1, day+1, QtCore.Qt.AlignCenter)

    def export(self):
        dia = QFileDialog(self, "Choose Where To Export")
        name = dia.getSaveFileName(directory="my_scan_result_export.taares",
                                   filter="Scan Result Export(*.taares);;All Files(*.*)")[0]
        if name:
            self.plot.export(name, lambda: print("Exported"))

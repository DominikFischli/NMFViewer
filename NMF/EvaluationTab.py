from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout, QWidget, QPushButton, QFileDialog
import pandas as pd
import numpy as np
import os

import spidet.utils.h5_utils as h5

from .utils.DataUtils import transform_time_grades, transform_triggers
from .utils.FileUtils import load_time_grades


class EvaluationTab(QWidget):
    timeGradesChanged = pyqtSignal(pd.DataFrame)
    triggersChanged = pyqtSignal(np.ndarray)
    toggleVPrime = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        self.load_time_grades_button = QPushButton("Load Time Grades (.csv) | (.h5)")
        self.load_time_grades_button.clicked.connect(self._load_time_grades_clicked)

        self.toggle_v_prime_button = QCheckBox(
            "Display difference to data matrix (V' = V - WH)"
        )
        self.toggle_v_prime_button.clicked.connect(self._toggle_difference)

        layout = QVBoxLayout()
        layout.addWidget(self.load_time_grades_button)
        layout.addWidget(self.toggle_v_prime_button)
        self.setLayout(layout)

    def _load_time_grades_clicked(self):
        time_grades_path = QFileDialog.getOpenFileName(
            self, "Load Time Grades", ".", "*.csv *.h5"
        )[0]
        time_grades = load_time_grades(time_grades_path)

        if os.path.splitext(time_grades_path)[1] == ".h5":
            self._check_for_triggers(time_grades_path)
        self.timeGradesChanged.emit(transform_time_grades(time_grades))

    def _toggle_difference(self):
        self.toggleVPrime.emit()

    def _check_for_triggers(self, path):
        trigs = h5.detect_triggers(path)
        self.triggersChanged.emit(trigs)

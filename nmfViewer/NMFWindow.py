from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QWidget,
)

import numpy as np

from NMF.NMFView import NMFView
from NMF.NMFTreeView import NMFFeatureMatrixItem, NMFModelItem
from NMF.Tabs import Tabs


class NMFWindow(QWidget):
    timeClicked = pyqtSignal(float, str)  # time, channel

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.start_time = 0

        self.v_prime = False
        self.v = None

        self.nmf_view = NMFView()
        self.nmf_view.cellClicked.connect(self._on_cell_clicked)
        self.tabs = Tabs()
        self.tabs.controls_tab.featureMatrixChanged.connect(
            self._feature_matrix_selected
        )
        self.tabs.controls_tab.nmfModelChanged.connect(self._nmf_model_selected)
        self.tabs.evaluation_tab.timeGradesChanged.connect(
            self.nmf_view.set_time_grades
        )
        self.tabs.evaluation_tab.triggersChanged.connect(self.nmf_view.set_triggers)
        self.tabs.evaluation_tab.toggleVPrime.connect(self._toggle_v_prime)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.nmf_view)
        self.setLayout(layout)

    def keyPressEvent(self, a0) -> None:
        if a0.key() == Qt.Key.Key_Right:
            self.move_forward()
        elif a0.key() == Qt.Key.Key_Left:
            self.move_backward()
        return super().keyPressEvent(a0)

    def move_forward(self):
        self.nmf_view.move_forward()

    def move_backward(self):
        self.nmf_view.move_backward()

    def show_v_prime(self):
        w = self.nmf_view.w_matrix()
        h = self.nmf_view.h_matrix()
        self.v = self.nmf_view.feature_matrix()
        v_prime = np.abs(self.v - w @ h)

        self.nmf_view.set_feature_matrix(v_prime, False)

    def show_v(self):
        self.nmf_view.set_feature_matrix(self.v)

    def _on_cell_clicked(self, time, channel):
        self.timeClicked.emit(time + self.start_time, channel)

    def _toggle_v_prime(self):
        self.v_prime = not self.v_prime
        self._update_feature_matrix()

    def _update_feature_matrix(self):
        if self.v_prime:
            self.show_v_prime()
        else:
            self.show_v()

    def _feature_matrix_selected(self, item: NMFFeatureMatrixItem):
        self._feature_matrix_item = item
        self.nmf_view.set_channel_names(item.load_channel_names())
        self.nmf_view.feature_matrix_sampling_frequency = item.load_sfreq()
        self.v = item.load_feature_matrix()
        self.start_time = item.load_start_timestamp()
        self._update_feature_matrix()

    def _nmf_model_selected(self, item: NMFModelItem):
        w = item.load_w()
        h = item.load_h()

        self.nmf_view.set_h_matrix(h)
        self.nmf_view.set_w_matrix(w)

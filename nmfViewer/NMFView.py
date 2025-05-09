from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsProxyWidget, QSizePolicy
from .Controls import ThresholdBox
from .MatrixView import MatrixView, MatrixHighlightView, pyqtSignal
from .FeatureMatrixView import FeatureMatrixView

import numpy as np
import pandas as pd

from pyqtgraph import GraphicsLayoutWidget, colormap, LinearRegionItem, mkPen
from pyqtgraph.functions import mkBrush


class NMFView(GraphicsLayoutWidget):
    cellClicked = pyqtSignal(float, str)  # time, channel

    def __init__(self, feature_matrix_sampling_frequency=50):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._fm_sfreq = feature_matrix_sampling_frequency

        # Some Variables
        self.min_frame_size = 210
        self.max_x_range = 600
        self.rank_factor = 30
        self.cm = colormap.get("CET-D1")
        self.setBackground("lightgrey")

        # Setup viewboxes
        #
        # H Viewbox
        self.vbh: MatrixView = MatrixHighlightView(colormap=self.cm)
        self.vbh.setMouseEnabled(x=True, y=False)
        self.plot_h = self.addPlot(row=0, col=1, viewBox=self.vbh)
        self.plot_h.hideAxis("left")
        self.plot_h.hideAxis("bottom")
        self.plot_h.showAxis("right")
        self.vbh.connect_scene_events()

        # W Viewbox
        self.vbw: MatrixView = MatrixView(
            enableMouse=False, colormap=self.cm, keep_range=False
        )
        self.plot_w = self.addPlot(row=1, col=0, viewBox=self.vbw)
        self.plot_w.hideAxis("left")
        self.vbw.connect_scene_events()
        self.vbw.cellClicked.connect(self.w_cell_selected)

        # Line length Viewbox
        self.vbfm: FeatureMatrixView = FeatureMatrixView(colormap=self.cm)
        self.plot_ll = self.addPlot(row=1, col=1, viewBox=self.vbfm)
        self.plot_ll.hideAxis("left")
        self.plot_ll.showAxis("right")
        self.vbfm.setMouseEnabled(x=True, y=False)
        self.vbfm.connect_scene_events()
        self.vbfm.cellClicked.connect(self.fm_cell_selected)

        # link axis
        self.vbfm.setXLink(self.vbh)
        self.vbfm.setYLink(self.vbw)

        # Fill items with dummy data
        self.rank = 4
        self.time_points = 2000
        self.channels = 112
        self.set_channel_names(["random"] * self.channels)

        # Add items to viewboxes
        self.vbh.set_matrix(np.random.normal(size=(self.time_points, self.rank)))
        self.vbw.set_matrix(np.random.normal(size=(self.rank, self.channels)))
        self.vbfm.set_matrix(np.random.normal(size=(self.time_points, self.channels)))

        # Add Control box for H thresholds
        self.control_box = ThresholdBox(self.vbh)
        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(self.control_box)
        self.proxy.setContentsMargins(0, 0, 0, 0)
        self.addItem(self.proxy, row=0, col=0)

        self.update_dimensions()

    @property
    def feature_matrix_sampling_frequency(self):
        return self._fm_sfreq

    @feature_matrix_sampling_frequency.setter
    def feature_matrix_sampling_frequency(self, value: int):
        self._fm_freq = value

    def set_h_matrix(self, data):
        data = data.T
        self.time_points, self.rank = data.shape

        self.update_dimensions()
        self.vbh.set_matrix(data)

    def h_matrix(self):
        return self.vbh.matrix.T[::3, :]

    def set_w_matrix(self, data):
        data = data.T
        self.channels = data.shape[0]
        self.vbw.set_matrix(data)

    def w_matrix(self):
        return self.vbw.matrix.T

    def set_feature_matrix(self, data, autolevels: bool | None = None):
        self.vbfm.set_matrix(matrix=data.T, autolevels=autolevels)

    def feature_matrix(self):
        return self.vbfm.matrix.T

    def set_channel_names(self, channel_names):
        self.channel_names = channel_names
        self.vbfm.channel_names = channel_names

    def set_time_grades(self, df: pd.DataFrame):
        for _index, row in df[df["Description"].str.startswith("IED")].iterrows():
            start = row["Onset"]
            stop = start + row["Duration"]
            self.paint_area(start, stop)

        for _index, row in df[df["Description"] == "NOISY"].iterrows():
            start = row["Onset"]
            stop = start + row["Duration"]
            self.paint_area(
                start,
                stop,
                brush_color=QColor(25, 237, 0, 10),
                pen_color=QColor(25, 237, 0, 80),
            )

    def set_triggers(self, triggers: np.ndarray):
        for start, stop in triggers:
            self.paint_area(
                start,
                stop,
                brush_color=QColor(133, 133, 133, 20),
                pen_color=QColor(170, 170, 170, 80),
            )

    def update_dimensions(self):
        new_max = max(self.min_frame_size, self.rank * self.rank_factor)

        # Set max width on W and max height on H
        self.plot_w.setMaximumWidth(new_max)
        self.plot_h.setMaximumHeight(new_max)

        self.vbw.setMaximumWidth(new_max)
        self.vbh.setMaximumHeight(new_max)

        # adjust the graphics proxy accordingly
        self.proxy.setMaximumWidth(new_max)
        self.proxy.setMaximumHeight(new_max)

    def paint_area(self, start, stop, brush_color=None, pen_color=None):
        if brush_color is None:
            brush_color = QColor(255, 255, 255, 10)
        if pen_color is None:
            pen_color = QColor(255, 255, 255, 80)

        brush = mkBrush(brush_color)
        pen = mkPen(pen_color, width=10)
        self.plot_h.addItem(
            LinearRegionItem((start, stop), movable=False, brush=brush, pen=pen)
        )
        self.plot_ll.addItem(
            LinearRegionItem((start, stop), movable=False, brush=brush, pen=pen)
        )

    def move_forward(self, percentage=0.2):
        self.vbh.move_forward(percentage)

    def move_backward(self, percentage=0.2):
        self.vbh.move_backward(percentage)

    def w_cell_selected(self, x, y):
        # Move view to center the highest value of the line length matrix
        # for which the w value multiplied with the corresponding h value contribute the most

        # e. g. w_ij was selected: find max x: h_xi * w_ij + C = ll_xi, ll_xi large, C small
        # as in h_xi * w_ij contribute the most to ll_xi

        # channel = i, h_row, w_col = j
        h_row = self.vbh.matrix[:, x]
        ll_row = self.vbfm.matrix[:, y]

        # get 100 largest ll_row values
        ll_desc_index = np.flip(np.argsort(ll_row))[:100]

        # on the difference between h and ll, chose those corresponding to large ll values
        candidates = (ll_row - h_row)[ll_desc_index]

        # the smaller the value, the larger the importance of w and h: chose smallest value as candidate
        candidate_index = np.argsort(candidates)[0]

        # remap onto index for coordinate
        x = ll_desc_index[candidate_index]

        # candidate_index = np.argmax(self.vbll.matrix[:, y])
        self.vbfm.center_x(x)

    def fm_cell_selected(self, x, y):
        time = x / self.feature_matrix_sampling_frequency
        channel = self.channel_names[y]
        self.cellClicked.emit(time, channel)

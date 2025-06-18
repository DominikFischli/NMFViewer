from PyQt6.QtWidgets import QGridLayout, QVBoxLayout
from .threshold_slider.ThresholdSlider import ThresholdSlider
from .MatrixView import MatrixHighlightView
from PyQt6.QtWidgets import QWidget

from functools import partial


class ThresholdBox(QWidget):
    """
    This class provides threshold sliders for a given matrix highlight view.
    """

    _grid: QGridLayout
    _matrix_view: MatrixHighlightView
    _thresholds: list[ThresholdSlider] = []

    def __init__(self, matrix_view: MatrixHighlightView) -> None:
        """

        Parameters
        ----------
        matrix_view : MatrixHighlightView
            The matrix view on which the threshold mask will be drawn.

        """
        super(ThresholdBox, self).__init__()

        self._grid = QVBoxLayout()
        self._grid.setContentsMargins(1, 1, 1, 1)
        self._grid.setSpacing(0)
        self.setLayout(self._grid)

        self._matrix_view = matrix_view
        self._matrix_view.matrixSet.connect(self._on_matrix_set)

    def _on_matrix_set(self):
        self._clear_thresholds()
        self._create_thresholds()

    def _create_thresholds(self):
        matrix = self._matrix_view.matrix
        rank = self._matrix_view.matrix.shape[1]
        max_height = int(self._matrix_view.height() / rank)
        for i in range(rank):
            threshold_slider = ThresholdSlider(matrix[:, i])
            threshold_slider.setMaximumHeight(max_height)
            self._thresholds.append(threshold_slider)

            threshold_slider.newEvents.connect(partial(self._on_new_threshold, i))
            self._grid.addWidget(threshold_slider)

            threshold_slider.newEvents.emit()

    def _on_new_threshold(self, row):
        threshold_slider = self.sender()
        self._matrix_view.set_highlight(threshold_slider.event_mask(), row)

    def _clear_thresholds(self):
        for i in reversed(range(len(self._thresholds))):
            self._grid.itemAt(i).widget().setParent(None)
        self._thresholds.clear()

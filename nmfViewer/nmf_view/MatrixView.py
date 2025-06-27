from typing import override
from PyQt6.QtCore import pyqtSignal

from pyqtgraph import TextItem, ViewBox, ImageItem, InfiniteLine
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
import numpy as np


class MatrixView(ViewBox):
    """
    This class holds and displays matrix data. Needs to be added to a `pyqtgraph` plot.

    Attributes
    ----------
    matrixSet : pyqtSignal
        This signal is emitted whenever the matrix has been set.
    cellClicked : pyqtSignal(int, int)
        This signal emits (x, y) coordinates on a mouse click
    autoLevels : bool
        This property determines if, when a new matrix is set, levels will be automatically calculated
        based on the matrix values.

    """

    matrixSet = pyqtSignal()
    cellClicked = pyqtSignal(int, int)

    _matrix_image_item = None
    _keep_range = True

    _value_text = None

    def __init__(
        self,
        parent=None,
        border=None,
        lockAspect=False,
        enableMouse=True,
        invertY=True,
        enableMenu=False,
        name=None,
        invertX=False,
        defaultPadding=0.0,
        colormap="CET-L17",
        keep_range=True,
    ):
        super().__init__(
            parent,
            border,
            lockAspect,
            enableMouse,
            invertY,
            enableMenu,
            name,
            invertX,
            defaultPadding,
        )

        self._keep_range = keep_range

        self._matrix_image_item = ImageItem(colorMap=colormap)
        self.addItem(self._matrix_image_item)

        self._vline = InfiniteLine(angle=90, movable=False, pen="black")
        self._hline = InfiniteLine(angle=0, movable=False, pen="black")
        self.addItem(self._vline, ignoreBounds=True)
        self.addItem(self._hline, ignoreBounds=True)

        self._value_text = TextItem("value: -", color=(0, 0, 0))
        self._value_text.setParentItem(self)

        self.show_crosshair = True
        self.show_value = True
        self.autoLevels = True

        self._matrix = np.array([])

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix

    @matrix.setter
    def matrix(self, data) -> None:
        self._matrix = data
        self._update_image()
        self.matrixSet.emit()

    @property
    def show_value(self) -> bool:
        return self._show_value

    @show_value.setter
    def show_value(self, visible: bool) -> None:
        self._show_value = visible

        if not visible:
            self._value_text.hide()

    @property
    def show_crosshair(self) -> bool:
        return self._show_crosshair

    @show_crosshair.setter
    def show_crosshair(self, visible: bool) -> None:
        self._show_crosshair = visible

        if not visible:
            self._vline.hide()
            self._hline.hide()

    def mouseClickEvent(self, ev: MouseClickEvent):
        x, y = self._matrix_position(ev.scenePos())

        if self._valid_matrix_position(x, y):
            self.cellClicked.emit(x, y)

        return super().mouseClickEvent(ev)

    def move_forward(self, percentage=0.2):
        self._move(percentage)

    def move_backward(self, percentage=0.2):
        self._move(percentage, -1)

    def center_x(self, x):
        width = self.viewRect().width()

        new_x = x - width // 2
        x_range = (new_x, new_x + width)

        self.setRange(xRange=x_range)

    def _connect_scene_events(self):
        self.scene().sigMouseMoved.connect(self._on_mouse_moved)

    def _matrix_position(self, scenePos):
        pos = self.mapSceneToView(scenePos)
        return int(pos.x()), int(pos.y())

    def _valid_matrix_position(self, x, y):
        rows, cols = self._matrix.shape
        return x < rows and y < cols and x >= 0 and y >= 0

    def _move(self, percentage=0.2, dir=1):
        x = self.viewRect().x()
        width = self.viewRect().width()

        change = percentage * width * dir
        x_range = (x + change, x + change + width)

        xmin, xmax = self.childrenBounds()[0]
        if x_range[0] < xmin:
            x_range = (xmin, xmin + width)
        elif x_range[1] > xmax:
            x_range = (xmax - width, xmax)

        self.setRange(xRange=x_range)

    def _on_mouse_moved(self, pos):
        if self.show_crosshair:
            self._update_crosshair(pos)
        else:
            self._vline.hide()
            self._hline.hide()

        if self.show_value:
            self._update_value(pos)
            self._value_text.show()
        else:
            self._value_text.hide()

    def _update_image(self):
        if self._keep_range and self._matrix_image_item.image is not None:
            self._set_image_and_retain_xrange()
        else:
            self._set_image()

    def _update_value(self, pos):
        mousePoint = self.mapSceneToView(pos)
        x = int(mousePoint.x())
        y = int(mousePoint.y())

        if self._valid_matrix_position(x, y):
            self._value_text.setText(f"value: {self._matrix[x, y]:1.2}")
        else:
            self._value_text.setText(f"value: -")

    def _update_crosshair(self, pos):
        self._vline.show()
        self._hline.show()

        bounding_rect = self.sceneBoundingRect()
        mousePoint = self.mapSceneToView(pos)

        if self.show_crosshair and self._valid_matrix_position(
            mousePoint.x(), mousePoint.y()
        ):
            self._vline.setPos(mousePoint.x())
            self._hline.setPos(mousePoint.y())
        elif (
            bounding_rect.x() <= pos.x()
            and bounding_rect.x() + bounding_rect.width() >= pos.x()
        ):
            self._hline.hide()
            self._vline.setPos(mousePoint.x())
        elif (
            bounding_rect.y() <= pos.y()
            and bounding_rect.y() + bounding_rect.height() >= pos.y()
        ):
            self._vline.hide()
            self._hline.setPos(mousePoint.y())
        else:
            self._vline.hide()
            self._hline.hide()

    def _set_image_and_retain_xrange(self):
        x = self.viewRect().x()
        width = self.viewRect().width()

        self._set_image()

        self.setRange(xRange=(x, x + width))

    def _set_image(self):
        self._matrix_image_item.setImage(self._matrix, autoLevels=self.autoLevels)

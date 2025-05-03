from PyQt6.QtCore import pyqtSignal

from pyqtgraph import TextItem, ViewBox, ImageItem, InfiniteLine, PlotItem
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
import numpy as np


class MatrixPlotItem(PlotItem):
    def __init__(
        self,
        parent=None,
        name=None,
        labels=None,
        title=None,
        viewBox=None,
        axisItems=None,
        enableMenu=True,
        **kargs,
    ):
        super().__init__(
            parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs
        )


class MatrixView(ViewBox):
    matrixSet = pyqtSignal()
    cellClicked = pyqtSignal(int, int)

    matrix = None
    matrix_image_item = None
    keep_range = True

    value_text = None

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
        colormap=None,
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

        self.keep_range = keep_range

        self.matrix_image_item = ImageItem(colorMap=colormap)
        self.addItem(self.matrix_image_item)

        self.vline = InfiniteLine(angle=90, movable=False, pen="w")
        self.hline = InfiniteLine(angle=0, movable=False, pen="w")
        self.addItem(self.vline, ignoreBounds=True)
        self.addItem(self.hline, ignoreBounds=True)

        self.value_text = TextItem("value: -", color=(255, 255, 255))
        self.value_text.setParentItem(self)

    def mouseClickEvent(self, ev: MouseClickEvent):
        x, y = self.matrix_position(ev.scenePos())

        if self.valid_matrix_position(x, y):
            self.cellClicked.emit(x, y)

        return super().mouseClickEvent(ev)

    def connect_scene_events(self):
        self.scene().sigMouseMoved.connect(self._on_mouse_moved)

    def _on_mouse_moved(self, pos):
        self.vline.show()
        self.hline.show()

        bounding_rect = self.sceneBoundingRect()
        mousePoint = self.mapSceneToView(pos)

        if bounding_rect.contains(pos):
            self.vline.setPos(mousePoint.x())
            self.hline.setPos(mousePoint.y())

            x = int(mousePoint.x())
            y = int(mousePoint.y())

            rows, cols = self.matrix.shape
            if x < rows and y < cols:
                self.value_text.setText(f"value: {self.matrix[x, y]}")

        elif (
            bounding_rect.x() <= pos.x()
            and bounding_rect.x() + bounding_rect.width() >= pos.x()
        ):
            self.hline.hide()
            self.vline.setPos(mousePoint.x())
        elif (
            bounding_rect.y() <= pos.y()
            and bounding_rect.y() + bounding_rect.height() >= pos.y()
        ):
            self.vline.hide()
            self.hline.setPos(mousePoint.y())
        else:
            self.vline.hide()
            self.hline.hide()

    def matrix_position(self, scenePos):
        pos = self.mapSceneToView(scenePos)
        return int(pos.x()), int(pos.y())

    def valid_matrix_position(self, x, y):
        rows, cols = self.matrix.shape
        return x < rows and y < cols

    def set_matrix(self, matrix):
        self.matrix = matrix
        self.update_image()
        self.matrixSet.emit()

    def update_image(self):
        if self.keep_range and self.matrix_image_item.image is not None:
            self._set_image_and_retain_xrange()
        else:
            self.matrix_image_item.setImage(self.matrix)

    def _set_image_and_retain_xrange(self):
        x = self.viewRect().x()
        width = self.viewRect().width()

        self.matrix_image_item.setImage(self.matrix)

        self.setRange(xRange=(x, x + width))

    def move(self, percentage=0.2, dir=1):
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

    def move_forward(self, percentage=0.2):
        self.move(percentage)

    def move_backward(self, percentage=0.2):
        self.move(percentage, -1)

    def center_x(self, x):
        width = self.viewRect().width()

        new_x = x - width // 2
        x_range = (new_x, new_x + width)

        self.setRange(xRange=x_range)


class MatrixHighlightView(MatrixView):
    highlight_matrix = None
    highlight_item: ImageItem = None

    # Highlight height can be from 1 to 3. Each row of the original matrix is repeated 3 times.
    # This procedure results in blazingly fast drawing
    highlight_height = 1

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
        defaultPadding=0,
        colormap=None,
        keep_range=True,
        row_height=3,
        highlight_height=1,
        color=(25, 237, 0),
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
            colormap,
            keep_range,
        )

        self.color = color
        self.row_height = row_height
        self.highlight_height = highlight_height

        self.highlight_item = ImageItem()  # Colors for highlights will be black, white.
        self.addItem(self.highlight_item)

    def set_matrix(self, matrix):
        self.n_cols, self.n_rows = matrix.shape
        matrix = matrix.repeat(
            self.row_height, axis=1
        )  # repeat axis 3 times such that highlights can be overlayed

        # setup highlight colors
        r, g, b = self.color
        colors = np.array([r, g, b, 0])  # RGBA format
        colors = colors[np.newaxis, :].repeat(self.n_cols, axis=0)
        colors = colors[:, np.newaxis, :].repeat(self.n_rows * self.row_height, axis=1)

        # Make the highlight matrix use RGBA format
        self.highlight_matrix = colors
        self.highlight_matrix = self.highlight_matrix
        self.highlight_item.setImage(self.highlight_matrix)

        # set matrix image
        super().set_matrix(matrix)

    def set_highlight(self, highlight_bitmap, row_index):
        highlight_bitmap = highlight_bitmap * 255
        self.highlight_matrix[:, (row_index * 3) + 2, 3] = highlight_bitmap
        self.highlight_item.updateImage()
        # self.highlight_item.setImage(self.highlight_matrix)

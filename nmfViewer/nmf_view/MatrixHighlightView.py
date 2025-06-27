import numpy as np

from pyqtgraph import ImageItem

from .MatrixView import MatrixView


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

    @property
    def matrix(self) -> np.ndarray:
        # return original data matrix
        return self._matrix[:, :: self.row_height]

    @matrix.setter
    def matrix(self, data) -> None:
        self.n_cols, self.n_rows = data.shape

        data = data.repeat(
            self.row_height, axis=1
        )  # repeat axis 3 times such that highlights can be overlayed
        # use axis=1 because of the way pyqtgraph interprets matrix data

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
        self._matrix = data
        self._update_image()
        self.matrixSet.emit()

    def set_highlight(self, highlight_bitmap: np.ndarray, row_index: int):
        highlight_bitmap = highlight_bitmap * 255
        self.highlight_matrix[:, (row_index * 3) + 2, 3] = highlight_bitmap
        self.highlight_item.updateImage()

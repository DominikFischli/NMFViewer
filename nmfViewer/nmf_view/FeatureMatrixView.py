from typing import override

from PyQt6.QtCore import QPointF
from pyqtgraph import TextItem
from .MatrixView import MatrixView


class FeatureMatrixView(MatrixView):
    """
    An extension to the matrix view which allows for channel names (row names) to be set.
    They will be displayed in an info panel next to the cursor if show_info is True.

    Attributes
    ----------
    show_info : bool
        Property determining whether channel names should be displayed
    channel_names : List[str]
        Channel names. Needs to correspond in size to the number of rows on the displayed matrix.

    """

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

        self.show_info = True
        self.channel_names = None
        self._info_panel = TextItem("info", color=(0, 0, 0))
        self.addItem(self._info_panel)
        self._info_panel.hide()

    @property
    def show_info(self) -> bool:
        return self._show_info

    @show_info.setter
    def show_info(self, visible: bool) -> None:
        self._show_info = visible

        if not visible:
            self._info_panel.hide()

    @override
    def _on_mouse_moved(self, pos):
        super()._on_mouse_moved(pos)
        if self.show_info:
            self._update_info_panel(pos)

    def _update_info_panel(self, pos):
        if not self.channel_names:
            return

        bounding_rect = self.sceneBoundingRect()
        if bounding_rect.contains(pos) and self.show_info:
            offset = QPointF(10, 0)
            text_width = self._info_panel.boundingRect().width()

            if pos.y() > bounding_rect.y() + bounding_rect.height() // 2:
                offset.setY(-20)
            if pos.x() > bounding_rect.x() + bounding_rect.width() // 2:
                offset.setX(-text_width)

            _, y = self._matrix_position(pos)
            y = min(y, len(self.channel_names) - 1)
            self._info_panel.setText(self.channel_names[y])

            text_pos = self.mapSceneToView(pos + offset)
            self._info_panel.show()
            self._info_panel.setPos(text_pos)
        else:
            self._info_panel.hide()

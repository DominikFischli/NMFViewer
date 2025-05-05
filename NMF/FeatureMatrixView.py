from typing import override

from PyQt6.QtCore import QPointF
from pyqtgraph import TextItem
from .MatrixView import MatrixView

class FeatureMatrixView(MatrixView):
    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True, invertY=True, enableMenu=False, name=None, invertX=False, defaultPadding=0, colormap=None, keep_range=True):
        super().__init__(parent, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX, defaultPadding, colormap, keep_range)

        self.info_panel = TextItem("info", color = (0, 0, 0))
        self.addItem(self.info_panel)
        self.info_panel.hide()

    @override
    def _on_mouse_moved(self, pos):
        super()._on_mouse_moved(pos)

        self.info_panel.hide()

        bounding_rect = self.sceneBoundingRect()

        if bounding_rect.contains(pos):
            offset = QPointF(10, 0)
            text_width = self.info_panel.boundingRect().width()

            if pos.y() > bounding_rect.y() + bounding_rect.height() // 2:
                offset.setY(-20)
            if pos.x() > bounding_rect.x() + bounding_rect.width() // 2:
                offset.setX(-text_width)



            text_pos = self.mapSceneToView(pos + offset)
            self.info_panel.show()
            self.info_panel.setPos(text_pos)
            self.info_panel.setText(f"{pos}")

            self.width()
            self.height()


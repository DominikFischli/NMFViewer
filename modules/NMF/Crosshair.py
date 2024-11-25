from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import PlotItem, InfiniteLine

class Crosshair(PlotItem):
    vline = None
    hline = None

    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)

        self.vline = InfiniteLine(angle=90, movable=False)
        self.hline = InfiniteLine(angle=0, movable=False)
        self.addItem(self.vline, ignoreBounds=True)
        self.addItem(self.hline, ignoreBounds=True)

    def connect_scene(self):
        self.scene().sigMouseMoved.connect(self._on_mouse_moved)

    def _on_mouse_moved(self, pos):
        print(pos)

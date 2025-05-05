from PyQt6.QtWidgets import QMainWindow
from NMF.NMFWindow import NMFWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(800,600,600,800)
        self.setWindowTitle("NMF Explorer")

        self.init_ui()

    def init_ui(self):
        widget = NMFWindow()
        self.setCentralWidget(widget)
        self.show()

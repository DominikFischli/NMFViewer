from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal

from PyQt6.QtCore import QModelIndex
from modules.NMF.NMFTreeView import NMFFeatureMatrixItem, NMFModelItem, NMFTreeView


class ControlsTab(QWidget):
    featureMatrixChanged = pyqtSignal(NMFFeatureMatrixItem)
    nmfModelChanged = pyqtSignal(NMFModelItem)

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.init_ui()
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    def init_ui(self):
        self.load_nmf_button = QPushButton("Load NMF Results")
        self.load_nmf_button.clicked.connect(self._load_nmf_clicked)

        self.nmf_tree_view = NMFTreeView()
        self.nmf_tree_view.clicked[QModelIndex].connect(self._tree_view_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.load_nmf_button)
        layout.addWidget(self.nmf_tree_view)
        self.setLayout(layout)

    def _load_nmf_clicked(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Load NMF(s)", ".", "*.h5")
        for file_name in file_names:
            self.nmf_tree_view.add_nmf_file(file_name)

    def _tree_view_clicked(self, index):
        item = self.nmf_tree_view.model().itemFromIndex(index)
        if isinstance(item, NMFFeatureMatrixItem):
            self.featureMatrixChanged.emit(item)
        elif isinstance(item, NMFModelItem):
            self.nmfModelChanged.emit(item)

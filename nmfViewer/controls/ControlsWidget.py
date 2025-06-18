from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal

from .ViewControls import ViewControls
from .NMFTreeView import NMFFeatureMatrixItem, NMFModelItem, NMFTreeView


class ControlsWidget(QWidget):
    """
    This widget allows the user to set the feature matrix and the nmf model.
    Additionally, it controls the display of the crosshair on the matrix views, the channel info label and the value info label.

    Should the user decide to change any of the above, a corresponding signal is emitted which can then be
    captured by the relevant widgets.

    Attributes
    ----------
    featureMatrixChanged : pyqtSignal(NMFFeatureMatrixItem)
        Emitted when the user selects a new feature matrix from the tree view.
    nmfModelChanged : pyqtSignal(NMFModelItem)
        Emitted when the user selects a NMF model from the tree view
    show_value : pyqtSignal(bool)
        Emitted when the user checks the show value box in the display controls
    show_crosshair : pyqtSignal(bool)
        Emitted when the user checks the show crosshair box in the display controls
    show_channel_info : pyqtSignal(bool)
        Emitted when the user checks the show channel info box in the display controls
    """

    featureMatrixChanged = pyqtSignal(NMFFeatureMatrixItem)
    nmfModelChanged = pyqtSignal(NMFModelItem)
    show_value = pyqtSignal(bool)
    show_crosshair = pyqtSignal(bool)
    show_channel_info = pyqtSignal(bool)

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._init_ui()
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

    def _init_ui(self):
        self.view_controls = ViewControls()
        self.view_controls.show_crosshair.connect(self.show_crosshair.emit)
        self.view_controls.show_channel_info.connect(self.show_channel_info.emit)
        self.view_controls.show_value.connect(self.show_value.emit)

        self.load_nmf_button = QPushButton("Load NMF Results")
        self.load_nmf_button.clicked.connect(self._load_nmf_clicked)

        self.nmf_tree_view = NMFTreeView()
        self.nmf_tree_view.featureMatrixChanged.connect(self.featureMatrixChanged.emit)
        self.nmf_tree_view.nmfModelChanged.connect(self.nmfModelChanged.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.load_nmf_button)
        layout.addWidget(self.nmf_tree_view)
        layout.addWidget(self.view_controls)
        self.setLayout(layout)

    def _load_nmf_clicked(self):
        file_names, _ = QFileDialog.getOpenFileNames(self, "Load NMF(s)", ".", "*.h5")
        for file_name in file_names:
            self.nmf_tree_view.add_nmf_file(file_name)

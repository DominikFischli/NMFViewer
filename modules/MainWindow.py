from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QFileDialog, QListView, QMainWindow, QPushButton, QGridLayout, QWidget, QAbstractItemView
from modules.NMF.NMFView import NMFView
from modules.utils.FileUtils import load_matrix, find_nmf_folders, load_time_grades
from modules.utils.DataUtils import transform_time_grades
from modules.MatrixListModel import MatrixListModel
#from modules.EvaluationFrame import EvaluationFrame

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.path = ''
        self.data_path = ''
        self.nmf_view = NMFView()

        self.meta_model = MatrixListModel()
        self.nmf_list_view = QListView()
        self.nmf_list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.nmf_list_view.setModel(self.meta_model)
        self.nmf_list_view.setMaximumWidth(200)
        self.nmf_list_view.setMaximumHeight(600)
        self.nmf_list_view.selectionModel().currentRowChanged.connect(self.nmf_selected)

        #self.evaluation_frame = EvaluationFrame()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(800,600,600,800)
        self.setWindowTitle("NMF Explorer")

        self.load_time_grades_button = QPushButton('Load Time Grades (.csv) | (.h5)')
        self.load_time_grades_button.clicked.connect(self.load_time_grades_clicked)

        self.load_results_folder_button = QPushButton('Load NMF Results Folder')
        self.load_results_folder_button.clicked.connect(self.load_results_folder_clicked)

        self.hide_button = QPushButton('<')
        self.hide_button.setMaximumSize(QSize(30,30))
        self.hide_button.clicked.connect(self._hide_selection_list)

        self.show_button = QPushButton('>')
        self.show_button.setMaximumSize(QSize(30,30))
        self.show_button.clicked.connect(self._show_selection_list)
        self.show_button.hide()

        self.load_line_length_button = QPushButton(text='Load Line Length Data')
        self.load_line_length_button.setDisabled(True)
        self.load_line_length_button.clicked.connect(self.load_line_length_clicked)

        layout = QGridLayout()
        layout.addWidget(self.hide_button, 0, 0)
        layout.addWidget(self.show_button, 0, 0)
        layout.addWidget(self.load_time_grades_button, 1, 0)
        layout.addWidget(self.load_results_folder_button, 2, 0)

        #layout.addWidget(self.evaluation_frame, 3, 0)

        layout.addWidget(self.nmf_list_view, 4, 0)
        layout.addWidget(self.load_line_length_button, 5, 0)

        layout.addWidget(self.nmf_view, 0, 1, 10, 10)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def _hide_selection_list(self):
        self.load_time_grades_button.hide()
        self.load_results_folder_button.hide()
        self.nmf_list_view.hide()
        self.load_line_length_button.hide()
        self.hide_button.hide()
        self.show_button.show()

    def _show_selection_list(self):
        self.load_time_grades_button.show()
        self.load_results_folder_button.show()
        self.nmf_list_view.show()
        self.load_line_length_button.show()

        self.show_button.hide()
        self.hide_button.show()

    def load_time_grades_clicked(self):
        time_grades_path = QFileDialog.getOpenFileName(self, 'Load Time Grades', '.', '*.csv *.h5')[0]
        time_grades = load_time_grades(time_grades_path)
        self.nmf_view.set_time_grades(transform_time_grades(time_grades))

    def load_results_folder_clicked(self):
        dir_path = QFileDialog.getExistingDirectory()
        self.meta_model.set_paths(find_nmf_folders(dir_path))

    def load_line_length_clicked(self):
        current_index = self.nmf_list_view.currentIndex()
        meta = self.meta_model.getMeta(current_index)
        self.nmf_view.set_line_length_matrix(load_matrix(meta.get_line_length_path()))

    def nmf_selected(self, current_index, _):
        meta = self.meta_model.getMeta(current_index)
        self.nmf_view.set_h_matrix(load_matrix(meta.h_path))
        self.nmf_view.set_w_matrix(load_matrix(meta.w_path))
        self.load_line_length_button.setEnabled(True)

    def keyPressEvent(self, a0) -> None:
        if a0.key() == Qt.Key.Key_Right:
            self.move_forward()
        elif a0.key() == Qt.Key.Key_Left:
            self.move_backward()
        return super().keyPressEvent(a0)

    def move_forward(self):
        self.nmf_view.move_forward()

    def move_backward(self):
        self.nmf_view.move_backward()

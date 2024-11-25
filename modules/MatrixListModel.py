from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt
import typing
import os
import re

class NMFMetaData():
    def __init__(self, path):
        self.path     = path
        self.rank     = re.search(r'k=(\d+)', path).groups()[0]
        self.sparsity = re.search(r's_(0.\d+)', path).groups()[0]
        self.h_path   = os.path.join(path, 'H_best.csv')
        self.w_path   = os.path.join(path, 'W_best.csv')

    def __str__(self) -> str:
        return f'{self.path.split("/")[-4]} -- rank: {self.rank}, sparsity: {self.sparsity}' 

    def get_line_length_path(self):
        return os.path.join(self.path, '../line_length.csv')

class MatrixListModel(QAbstractListModel):
    def __init__(self, *args, paths=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta_data = []

    def set_paths(self, paths):
        for path in paths:
            if 'k=' in path:
                self.meta_data.append(NMFMetaData(path))
        self.layoutChanged.emit()

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.meta_data[index.row()])

    def getMeta(self, index: QModelIndex):
        return self.meta_data[index.row()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.meta_data)

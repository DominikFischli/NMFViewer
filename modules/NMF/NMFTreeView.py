import os
from PyQt6.QtCore import QAbstractItemModel, QAbstractListModel, QModelIndex
from PyQt6.QtGui import QFileSystemModel, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QTreeView, QWidget
import typing

from spidet.save.nmf_data import NMFData


class NMFTreeView(QTreeView):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        model = QStandardItemModel()
        self.rootItem = model.invisibleRootItem()
        self.setModel(model)

    def add_nmf_file(self, path: str) -> None:
        filename = os.path.basename(path)
        fileItem = QStandardItem(filename)
        fileItem.setSelectable(False)
        self.rootItem.appendRow(fileItem)

        data = NMFData(path)
        for fm in data.list_feature_matrices():
            fmItem = NMFFeatureMatrixItem(data, fm)
            fileItem.appendRow(fmItem)

            for rank in data.list_ranks(fm):
                rankItem = QStandardItem(str(rank))
                rankItem.setSelectable(False)
                fmItem.appendRow(rankItem)

                for model in data.list_models(fm, rank):
                    modelItem = NMFModelItem(data, fm, rank, model)
                    rankItem.appendRow(modelItem)


class NMFFeatureMatrixItem(QStandardItem):
    def __init__(self, data: NMFData, feature_matrix: str) -> None:
        super().__init__(feature_matrix)
        self.data = data
        self.feature_matrix = feature_matrix

    def load_feature_matrix(self):
        return self.data.feature_matrix(self.feature_matrix)

    def load_channel_names(self):
        return self.data.channel_names(self.feature_matrix)


class NMFModelItem(QStandardItem):
    def __init__(
        self, data: NMFData, feature_matrix: str, rank: str, model: str
    ) -> None:
        super().__init__(model)
        self.data = data
        self.feature_matrix = feature_matrix
        self.rank = rank
        self.model = model

    def load_nmf(self):
        return self.data.nmf(self.feature_matrix, self.rank, self.model)

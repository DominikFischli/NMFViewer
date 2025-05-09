import os
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QTreeView, QWidget
import typing

from spidet.save.nmf_data import NMFRoot, FeatureMatrixGroup, NMFModel


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

        data = NMFRoot(path)
        for dset_label in data.datasets():
            dset = data.dataset(dset_label)
            for fm_name in dset.feature_matrices():
                fm_group = dset.feature_matrix(fm_name)
                start_timestamp = dset.meta().start_timestamp

                fmItem = NMFFeatureMatrixItem(fm_group, start_timestamp)
                fileItem.appendRow(fmItem)

                for rank in fm_group.ranks():
                    rank_group = fm_group.by_rank(rank)
                    rankItem = QStandardItem(rank)
                    rankItem.setSelectable(False)
                    fmItem.appendRow(rankItem)

                    for model_name in rank_group.models():
                        model = rank_group.model(model_name)
                        modelItem = NMFModelItem(model)
                        rankItem.appendRow(modelItem)


class NMFFeatureMatrixItem(QStandardItem):
    def __init__(self, fm_group: FeatureMatrixGroup, start_timestamp) -> None:
        super().__init__(fm_group.name)
        self.feature_matrix_group = fm_group
        self.start_timestamp = start_timestamp

    def load_feature_matrix(self):
        return self.feature_matrix_group.feature_matrix

    def load_channel_names(self):
        return self.feature_matrix_group.feature_names

    def load_sfreq(self):
        return self.feature_matrix_group.sfreq

    def load_start_timestamp(self):
        return self.start_timestamp


class NMFModelItem(QStandardItem):
    def __init__(self, model: NMFModel) -> None:
        super().__init__(model.name)
        self.model = model

    def load_w(self):
        return self.model.w

    def load_h(self):
        return self.model.h

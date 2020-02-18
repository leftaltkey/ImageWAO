
from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import QImageGridModel, UserRoles

class QImageGridView(QtWidgets.QTableView):

    # TODO: Add new signals to be more specific -- e.g.
    # selectedFilesChanged = QtCore.Signal(Path) # this prevents redundant signal emits
    # selectedImageChanged = QtCore.Signal(QImage) # this will let the grid determine what the viewer shows

    # Convenience signal    
    selectedIndexesChanged = QtCore.Signal(list)

    def __init__(self):
        super().__init__()
        self.setModel(QImageGridModel())

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.selectionModel().selectionChanged.connect(self._emitSelectionChanged)

    def _emitSelectionChanged(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()
        self.selectedIndexesChanged.emit(indexes)

    def selectFile(self, path):
        ''' Selects all the items associated
        with a given file path
        '''
        self.selectionModel().clearSelection()
        indexes = self.model().matchPath(path)
        for idx in indexes:
            self.selectionModel().select(idx, QtCore.QItemSelectionModel.Select)

        # Ensure the newly selected index is visible
        try:
            idx = indexes[0]
        except IndexError:
            print(f'No indexes were found matching the requested path: {path}')
        else:
            self.scrollTo(idx)
            # selectedImageChanged.emit(idx.data(role=UserRoles.EntireImage))


if __name__ == '__main__':
    pass

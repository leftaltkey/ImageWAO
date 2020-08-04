from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from transects import TransectSaveData
from serializers import JSONDrawnItems

from .gridmodel import QImageGridModel, UserRoles
from .merging import MergedIndexes
from .delegates import ImageDelegate


class QImageGridView(QtWidgets.QTableView):

    selectedFilesChanged = QtCore.Signal(Path)  # this prevents redundant signal emits
    selectedImageChanged = QtCore.Signal(
        QtGui.QImage, JSONDrawnItems
    )  # Send image/drawings to display
    notificationMessage = QtCore.Signal(str)  # notifications to the main application
    statusMessage = QtCore.Signal(tuple)  # status bar message to the main application
    loadProgress = QtCore.Signal(int)  # loading progress notification
    loadFinished = QtCore.Signal()  # loading finished notification
    countDataChanged = QtCore.Signal(TransectSaveData)

    def __init__(self):
        super().__init__()
        self.setModel(QImageGridModel())
        self.setItemDelegate(ImageDelegate())

        # Hide headers
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        # Resize headers to fit the contents
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )
        self.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )

        # Create context menu
        self.menu = QtWidgets.QMenu(self)
        self._populateContextMenu()

        # Context menu policy must be CustomContextMenu for us to implement
        # our own context menu. Connect the context menu request to our internal slot.
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)

        # Handle selection changes and map to appropriate signals
        self.selectionModel().selectionChanged.connect(self._handleSelectionChange)

        # Bubble progress and message updates from the model
        # (The model often has to perform expensive loading operations)
        self.model().loadProgress.connect(self.loadProgress.emit)
        self.model().loadFinished.connect(self.loadFinished.emit)
        self.model().message.connect(self.statusMessage.emit)
        self.model().transectDataChanged.connect(self.countDataChanged.emit)

        # Keep track of when we last sent out a previewed image
        # (generated by the index merger)
        # This is used when we need to save drawings and animal
        # counts, but need to know which images the drawings/counts
        # were actually on.
        self._mergedIndexes = None

    def _populateContextMenu(self):
        # Create context menu
        self.menu = QtWidgets.QMenu(self)

        # Create menu actions
        previewAction = QtWidgets.QAction("Preview", self)

        # Connect handlers for actions
        previewAction.triggered.connect(self._handlePreviewRequest)

        # Add actions to the menu
        self.menu.addAction(previewAction)

    def clear(self):
        self.model().resetImagesFromFullImages([])

    @QtCore.Slot(QtCore.QPoint)
    def _customMenuRequested(self, pos: QtCore.QPoint):
        """
        Open the context menu
        """
        self.menu.popup(self.viewport().mapToGlobal(pos))

    @QtCore.Slot(str)
    def addFolder(self, folder):
        """
        Adds the folder at this directory to the model,
        removing any other model that may have been previously loaded.
        folder: any Path() -able object, resolving to a directory.
        """
        self.model().tryAddFolder(folder)

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _handleSelectionChange(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Since the selection has changed, we cannot be dealing
        # with a preview request.
        self._mergedIndexes = None

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the first of the selected indexes
        index = indexes[0]
        if index.isValid():

            # Get the image to be displayed, and the items drawn on it
            img = index.data(role=UserRoles.FullResImage)
            items = index.data(role=UserRoles.DrawnItems)

            # Note: items will be "None" if there are none set.
            self.selectedImageChanged.emit(img, items)

        # Emit the files that are currently selected
        files = [idx.data(role=UserRoles.ImagePath) for idx in indexes]
        self.selectedFilesChanged.emit(files)

    @QtCore.Slot()
    def _handlePreviewRequest(self):
        """
        Requests a preview of all selected images
        from the model, emitting that in the selectedImageChanged
        signal
        """

        # Currently selected indexes
        indexes = self.selectionModel().selectedIndexes()

        # Nothing to do if nothing is selected
        if len(indexes) == 0:
            return

        # Merge the indexes togther, create a preview image
        self._mergedIndexes = MergedIndexes(indexes)
        preview = self._mergedIndexes.resultantImage()

        # Merge drawn items
        mergedItems: JSONDrawnItems = self._mergedIndexes.drawnItems()

        # Emit data
        self.selectedImageChanged.emit(preview, mergedItems)

    @QtCore.Slot(str)
    def selectFile(self, path):
        """
        Selects all the items associated
        with a given file path
        """
        self.selectionModel().clearSelection()
        indexes = self.model().matchPath(path)
        for idx in indexes:
            self.selectionModel().select(idx, QtCore.QItemSelectionModel.Select)

        try:
            idx = indexes[0]
        except IndexError:
            self.notificationMessage.emit(
                "Images still loading...\n\n"
                f"No image parts were found at the requested path:\n{path}"
            )
        else:

            # Ensure the index associated with this file is visible
            self.scrollTo(idx)

            # Select the entire image associated with the first index
            self._handlePreviewRequest()

    @QtCore.Slot(JSONDrawnItems)
    def setDrawings(self, drawings: JSONDrawnItems):
        """
        Set the drawn items passed in to the currently active
        model index.
        """
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # If only we haven't merged any indexes together,
        # save the drawn items to the first selected index
        if self._mergedIndexes is None:
            index = indexes[0]
            self.model().setDrawings(index, drawings)

        # If multiple indexes are merged, we need to
        # sort out which items belong where
        else:

            # Assign items to specific indexes.
            # Account for coordinate transformations
            self._mergedIndexes.setModelDrawings(self.model(), drawings)

    @QtCore.Slot()
    def save(self):
        """
        Save the model.
        """
        self.model().save()

    @QtCore.Slot()
    def computeTransectData(self):
        data = self.model().transectData()
        if data is not None:
            self.model().transectDataChanged.emit(data)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        self.model().setDisplayWidth(event.size().width())
        super().resizeEvent(event)


if __name__ == "__main__":
    pass

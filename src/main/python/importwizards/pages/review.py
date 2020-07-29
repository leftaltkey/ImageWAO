
from PySide2 import QtCore, QtWidgets, QtGui

# TODO don't allow invalid path characters in the transect name
# TODO button to toggle numeric or alpha bravo etc
from ..transecttable import Transect, TransectTableModel, TransectTableView

from .ids import PageIds

class ReviewPage(QtWidgets.QWizardPage):

    modelChanged = QtCore.Signal(TransectTableView)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Review')
        self.topLabel = QtWidgets.QLabel(
            'These are the categorized transects, in chronological order.\n'
            'Note that the geographical order, often given North to South as Alpha, Bravo, etc. '
            'is not necessarily the same as the chronological order.\n\n'
            'Copy and paste the correct naming order from Excel, or enter the names manually.\n'
        )
        self.topLabel.setWordWrap(True)

        # Loading widgets
        self.loadingLabel = QtWidgets.QLabel('Categorizing images...')
        self.progressBar = QtWidgets.QProgressBar(self)

        self.view = TransectTableView()
        self.model = TransectTableModel()
        self.model.categorizeProgress.connect(self.progressBar.setValue)
        self.model.categorizeComplete.connect(self._categorizeComplete)

        self.view.setModel(self.model)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.topLabel)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Initally the categorization has not finished
        self._categorizationFinished = False

    @QtCore.Slot()
    def _categorizeComplete(self):
        self.loadingLabel.setText('Categorizing images... Complete')

        # Tell the page that it is complete so it can update the correct buttons.
        self._categorizationFinished = True
        self.completeChanged.emit()

        # Ensure that the model gets renamed nicely, and share it with the other pages
        self.model.renameByOrder()
        self.modelChanged.emit(self.model)

        # Adjust the size of the wizard to fit in the new data
        self.wizard().adjustSize()
        self.view.resizeColumnsToContents()

    def isComplete(self):
        return self._categorizationFinished

    def initializePage(self):

        # read data from previous fields
        folder = self.field('importFolder')
        maxDelay = self.field('maxDelay')
        minCount = self.field('minCount')

        # read folder
        self.model.clearData()
        self.model.readFolder(folder, maxDelay, minCount)
    
    def nextId(self):
        return PageIds.Page_Metadata

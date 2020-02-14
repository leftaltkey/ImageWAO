
from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from .address import AddressBar
from tools import clearLayout


class Library(QtWidgets.QWidget):

    def __init__(self, ctx):
        super().__init__()

        # context
        self.ctx = ctx

        # root path
        settings = QtCore.QSettings()
        rootPath = settings.value(
            'library/homeDirectory',
            None
        )

        if rootPath is None:
            self.pathNotDefined()
        else:
            self.rebase(rootPath)

    def pathNotDefined(self):
        
        # prompt user to choose a flights folder
        button = QtWidgets.QPushButton('Choose Flights Folder')
        button.clicked.connect(self.chooseRootFolder)

        # add to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

        # note the root path
        self.rootPath = None

    def chooseRootFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            'Choose Flight Folder',
            Path().home().anchor,
            QtWidgets.QFileDialog().ShowDirsOnly
        )

        if not folder == '':

            # remove old layout
            clearLayout(self.layout())

            # rebase view on new folder
            self.rebase(folder)

            # save this root path
            QtCore.QSettings().setValue('library/homeDirectory', folder)

    def rebase(self, rootPath):

        # file model
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(rootPath)

        # file view
        self.view = QtWidgets.QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(rootPath))

        # connection to update view window from view window interaction
        self.view.activated.connect(self.viewActivated)

        # address bar
        self.address = AddressBar(self.ctx)
        self.address.home_path = self.model.rootDirectory()
        self.address.path = self.model.rootDirectory()

        # connection to update view window based on address bar
        self.address.activated.connect(self.addressActivated)

        # layout init
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,5,0,0)

        # add layout items
        self.layout().addWidget(self.address)
        self.layout().addWidget(self.view, stretch=1)

        # note the root path
        self.rootPath = rootPath

    def viewActivated(self, index):
        if self.model.fileInfo(index).isDir():
            self.view.setRootIndex(index)
            self.address.path = QtCore.QDir(self.model.filePath(index))

    def addressActivated(self, path):
        index = self.model.index(path)
        self.viewActivated(index)

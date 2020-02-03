

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide2 import ApplicationContext

from PySide2.QtWidgets import (
    QGraphicsView, QScrollArea,
)

from imagewao import QImageWAO
from library import Library

class AppContext(ApplicationContext):

    @cached_property
    def window(self):
        return QImageWAO(
            self.mspaint,
            self.grid,
            self.library,
            self.animalAdder,
            self.animalTotals,
        )

    @cached_property
    def mspaint(self):
        return QGraphicsView()

    @cached_property
    def grid(self):
        return QScrollArea()

    @cached_property
    def library(self):
        return Library(self)

    @cached_property
    def animalAdder(self):
        return QScrollArea()

    @cached_property
    def animalTotals(self):
        return QScrollArea()
    
    def run(self):
        self.window.resize(650, 350)
        self.window.show()
        return self.app.exec_()
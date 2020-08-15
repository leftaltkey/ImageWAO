from pathlib import Path
from typing import List

from PySide2 import QtWidgets, QtGui, QtCore

from .person import Person
from .transect import Transect


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        buttonBox = QtWidgets.QDialogButtonBox()
        addPersonButton = buttonBox.addButton(
            "Add Person", QtWidgets.QDialogButtonBox.ResetRole
        )
        okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)

        addPersonButton.clicked.connect(lambda: self._addPerson())
        okayButton.clicked.connect(self._okPressed)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def _addPerson(self, name: str = "New Person") -> Person:
        person = Person(name)
        self.layout().insertWidget(self.layout().count() - 1, person)
        return person

    @QtCore.Slot()
    def _okPressed(self):
        # would want to save here
        self.close()

    def _clearPeople(self):
        """Clears all people from layout, leaving button box"""
        layout = self.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if not item:
                continue

            w = item.widget()
            if w and isinstance(w, Person):
                item = layout.takeAt(i)
                w.deleteLater()

    def _people(self) -> List[Person]:
        people = []
        layout = self.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if not item:
                continue

            w = item.widget()
            if w and isinstance(w, Person):
                people.append(w)
        return people

    def readFlightFolder(self, flightFolder: Path):

        self._clearPeople()

        transects = Transect.createFromFlight(flightFolder)
        transects.extend(transects)
        transects.sort(key=lambda x: x.numPhotos)

        self._addPerson("Lauren")
        self._addPerson("Noah")
        self._addPerson("Matt")

        people = self._people()
        people.reverse()  # want people top to bottom
        numPeople = len(people)
        i = 0
        while transects:
            personIndex = i % numPeople
            person = people[personIndex]
            person.addTransect(transects.pop())
            i += 1

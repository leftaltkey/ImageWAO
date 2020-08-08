from PySide2 import QtWidgets, QtCore

from .ids import PageIds

from ...flightinfoform import FlightInfoForm

# TODO save to file and allow user to view/edit later (right click on folder name?)
# TODO right click on flight folder for a few options:
#   view distribution
#   view migration report
#   view meta data


class MetadataPage(QtWidgets.QWizardPage):

    flightInfoChanged = QtCore.Signal(FlightInfoForm)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Metadata")
        self.setSubTitle(
            "Include metadata about the flight. "
            "This will be saved alongside the transect images."
        )

        # Copy the layout of the flight info form
        self._flightInfoForm = FlightInfoForm()
        self.setLayout(self._flightInfoForm.layout())

        self.registerField("flightInfoForm", self._flightInfoForm)

    def _saveDefaults(self):
        self.flightInfoChanged.emit(self._flightInfoForm)

    def nextId(self):
        return PageIds.Page_SetLibrary

from silx.gui import qt
from ..common.master_file_widget import MasterFileWidget
from .geometry_parameters import GeometryParameterGroupBox


class GeometryTransformationSettings(qt.QWidget):
    sigParametersChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geometry Transformation Parameters")
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        layout = qt.QVBoxLayout()
        self._masterGroup = qt.QGroupBox(self)
        masterLayout = qt.QFormLayout(self._masterGroup)
        self._geometryFileWidget = MasterFileWidget(
            dialogTitle="3DXRD Experiment Master File"
        )
        masterLayout.addRow("Geometry Parameter File:", self._geometryFileWidget)
        layout.addWidget(self._masterGroup)
        self._geoParameterGroup = GeometryParameterGroupBox(self)
        layout.addWidget(self._geoParameterGroup)
        self.setLayout(layout)

        self._geometryFileWidget.sigMasterFileChanged.connect(self._setUpGeoParams)

    def _setUpGeoParams(self, filePath: str):
        self._geoParameterGroup.fillGeometryValues(filePath=filePath)

    def getGeometryFile(self, filePath: str):
        self._geoParameterGroup.getGeometryParameterAsParFile(filePath)

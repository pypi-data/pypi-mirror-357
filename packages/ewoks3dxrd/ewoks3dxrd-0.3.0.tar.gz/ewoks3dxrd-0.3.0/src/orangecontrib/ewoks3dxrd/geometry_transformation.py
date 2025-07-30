from pathlib import Path

from ewoksorange.bindings import OWEwoksWidgetOneThread
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.io.utils import DataUrl

from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.tasks.geometry_transformation import GeometryTransformation

from .common.utils import Ewoks3DXRDPlot2D
from .geometry.geometry_transformation_settings import GeometryTransformationSettings


class OWGeometryTransformation(
    OWEwoksWidgetOneThread, ewokstaskclass=GeometryTransformation
):
    name = "Geometry Transformation"
    description = (
        "Generate ds, g-vectors, eta, etc on detector corrected segmented 3D Peaks."
    )
    icon = "icons/settings.svg"
    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        self._settingsPanelWidget = qt.QWidget(self)
        settingLayout = qt.QVBoxLayout(self._settingsPanelWidget)

        self._settingsPanel = GeometryTransformationSettings(self)
        scrollArea = qt.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self._settingsPanel)
        settingLayout.addWidget(scrollArea)

        executeOverWriteLayout = qt.QFormLayout()
        self._detector_corrected_url = qt.QLineEdit()
        self._overwrite = qt.QCheckBox()
        self._computeGeometryCalculationBtn = qt.QPushButton(
            "Compute Geometry Vectors for Peaks"
        )
        executeOverWriteLayout.addRow(
            "Input: Detector Corrected URL", self._detector_corrected_url
        )
        executeOverWriteLayout.addRow("Overwrite", self._overwrite)
        executeOverWriteLayout.addRow(self._computeGeometryCalculationBtn)
        settingLayout.addLayout(executeOverWriteLayout)
        self._computeGeometryCalculationBtn.clicked.connect(
            self._executeGeometryCalculation
        )

        self._plot = Ewoks3DXRDPlot2D(self)
        self._plot.setKeepDataAspectRatio(False)
        self._plot.getColorBarWidget().setVisible(False)
        self.splitter = qt.QSplitter(qt.Qt.Horizontal)
        self.splitter.addWidget(self._settingsPanelWidget)
        self.splitter.addWidget(self._plot)
        self.splitter.setSizes([300, 700])  # Adjust default widths

        self.mainArea.layout().addWidget(self.splitter)
        self._settingsPanel.setSizePolicy(
            qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred
        )
        self._plot.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        self._has_recent_update: bool = False

    def handleNewSignals(self):
        self._input_detector_corrected_peaks_url = self.get_task_input_value(
            "spatial_corrected_data_url"
        )
        self._detector_corrected_url.setText(self._input_detector_corrected_peaks_url)

    def _executeGeometryCalculation(self):
        try:
            self._validateInputs()
            geometry_file = self._prepareGeometryFile()
            self.set_dynamic_input("overwrite", self._overwrite.isChecked())
            self.set_dynamic_input("geometry_par_file", str(geometry_file))
            self.execute_ewoks_task()
        except Exception as e:
            self._showError(str(e))

    def task_output_changed(self):
        if self.task_exception:
            self._showError(message=str(self.task_exception))
            return

        if self.get_task_output_value("geometry_updated_data_url") is None:
            return

        data_url = DataUrl(self.get_task_output_value("geometry_updated_data_url"))
        nexus_file_path, geometry_data_group_path = (
            data_url.file_path(),
            data_url.data_path(),
        )
        geo_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=geometry_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=geo_3d_peaks["ds"],
            y=geo_3d_peaks["eta"],
            value=geo_3d_peaks["Number_of_pixels"],
            colormap=Colormap(
                name="viridis", normalization="log", autoscaleMode="percentile_1_99"
            ),
            symbol="o",
            legend="aligned Peaks",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphXLabel("Reciprocal distance (ds)")
        self._plot.setGraphYLabel("Azimuthal angle (eta)")
        self._plot.resetZoom()

    def _validateInputs(self):
        input_url = self._detector_corrected_url.text().strip()
        if not input_url:
            raise ValueError("No detector corrected data URL to process.")

    def _prepareGeometryFile(self) -> Path:
        file_path = Path(DataUrl(self._detector_corrected_url.text()).file_path())
        geometry_file = file_path.parent / "geometry_tdxrd.par"
        self._settingsPanel.getGeometryFile(filePath=str(geometry_file))
        return geometry_file

    def _showError(self, message: str):
        qt.QMessageBox.critical(self, "Geometry Error", message)

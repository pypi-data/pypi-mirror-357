from __future__ import annotations

import numpy as np
from ewoksorange.bindings import OWEwoksWidgetNoThread
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.io.utils import DataUrl

from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.tasks.detector_spatial_correction import DetectorSpatialCorrection

from .common.utils import Ewoks3DXRDPlot2D
from .detector.detector_correction_settings import DetectorCorrectionSettings


class OWDetectorCorrection(
    OWEwoksWidgetNoThread, ewokstaskclass=DetectorSpatialCorrection
):
    name = "Detector Correction"
    description = "Correct spatial deformed detector into plane"
    icon = "icons/distortion_plane.svg"
    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        self._plot = Ewoks3DXRDPlot2D(self)
        self._plot.getColorBarWidget().setVisible(False)

        settings_panel_widget = qt.QWidget(self)
        setting_layout = qt.QVBoxLayout(settings_panel_widget)
        self._settings_widget = DetectorCorrectionSettings()

        action_layout = qt.QFormLayout()
        self._segmenter_url = qt.QLineEdit()
        self._overwrite = qt.QCheckBox("Overwrite")
        execute_btn = qt.QPushButton("Execute Detector Correction")
        execute_btn.clicked.connect(self._on_execute_det_correction)
        action_layout.addRow("Segmented URL", self._segmenter_url)
        self._segmenter_url.textChanged.connect(self._drawInputSegmentedPeaks)
        action_layout.addWidget(self._overwrite)
        action_layout.addWidget(execute_btn)

        setting_layout.addWidget(self._settings_widget, stretch=1)
        setting_layout.addLayout(action_layout)

        splitter = qt.QSplitter(qt.Qt.Horizontal)
        splitter.addWidget(settings_panel_widget)
        splitter.addWidget(self._plot)
        splitter.setSizes([300, 700])
        self.mainArea.layout().addWidget(splitter)

    def getDetectorSettings(self):
        params = self._settings_widget.getParameters()
        return {**params, "overwrite": self._overwrite.isChecked()}

    def handleNewSignals(self):
        self._input_segmented_peaks_url = self.get_task_input_value(
            "segmented_peaks_url"
        )
        self._segmenter_url.setText(self._input_segmented_peaks_url)
        self._drawInputSegmentedPeaks()

    def _drawInputSegmentedPeaks(self):
        data_url = DataUrl(self._segmenter_url.text().strip())
        nexus_file_path = data_url.file_path()
        segmented_data_group_path = data_url.data_path()

        segmented_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=segmented_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=segmented_3d_peaks["f_raw"],
            y=segmented_3d_peaks["s_raw"],
            value=np.ones(len(segmented_3d_peaks["f_raw"])),
            colormap=Colormap(
                colors=np.array(
                    [
                        [0.0, 0.0, 1.0],
                    ],
                    dtype=np.float32,
                )
            ),
            symbol="o",
            legend="rawPixels",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphXLabel("fast column")
        self._plot.setGraphYLabel("slow column")
        self._plot.setGraphTitle("Raw Pixels O (blue)")
        self._plot.resetZoom()

    def _on_execute_det_correction(self):

        try:
            self._validateInputs()
            params = self.getDetectorSettings()
            params = {
                **params,
                "segmented_peaks_url": self._segmenter_url.text().strip(),
            }
            self.update_default_inputs(**params)
            self.execute_ewoks_task()
        except Exception as e:
            self._showError(str(e))

    def task_output_changed(self):
        data_url = DataUrl(self.get_task_output_value("spatial_corrected_data_url"))
        nexus_file_path = data_url.file_path()
        detector_data_group_path = data_url.data_path()

        det_corrected_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=detector_data_group_path,
        )
        scatter = self._plot.addScatter(
            x=det_corrected_3d_peaks["fc"],
            y=det_corrected_3d_peaks["sc"],
            value=np.ones(len(det_corrected_3d_peaks["fc"])),
            colormap=Colormap(
                colors=np.array(
                    [
                        [1.0, 0.0, 0.0],
                    ],
                    dtype=np.float32,
                )
            ),
            symbol="+",
            legend="corrected Pixels",
        )
        scatter.setSymbolSize(7)
        self._plot.setGraphTitle("Raw Pixels O  (blue) vs Corrected Pixels + (red)")
        self._plot.resetZoom()

    def _showError(self, message: str):
        qt.QMessageBox.critical(self, "Detector Correction Error", message)

    def _validateInputs(self):
        input_url = self._segmenter_url.text().strip()
        if not input_url:
            raise ValueError("No segmenter data URL to process.")

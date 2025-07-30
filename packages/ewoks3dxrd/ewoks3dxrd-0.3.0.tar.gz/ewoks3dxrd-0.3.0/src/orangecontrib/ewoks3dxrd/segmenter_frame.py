from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import qtawesome
from ewoksorange.bindings import OWEwoksWidgetOneThread
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.qt import QSizePolicy, QSplitter, Qt
from silx.io.utils import DataUrl

from ewoks3dxrd.io import get_frame_image, get_monitor_scale_factor_for_frame_index
from ewoks3dxrd.nexus.peaks import read_peaks_attributes
from ewoks3dxrd.segment import segment_frame
from ewoks3dxrd.tasks.segment_scan import SegmentScan

from .common.utils import Ewoks3DXRDPlot2D
from .segment.dual_plot_silx import SilxSyncDualPlot
from .segment.segmenter_settings import SegmenterSettings
from .segment.utils import ask_confirmation_to_repeat_segmentation


class OWFrameSegmenter(OWEwoksWidgetOneThread, ewokstaskclass=SegmentScan):
    name = "Peaks Segmentation"
    description = "Runs segmentation on a scan, with preview on a frame."
    icon = "icons/filter_frames.svg"
    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        # --- Create the full settings panel on the left ---
        self.settings_panel_widget = qt.QWidget(self)
        setting_layout = qt.QVBoxLayout(self.settings_panel_widget)

        self.settings_panel = SegmenterSettings(self)
        self.settings_panel.sigParametersChanged.connect(self.display_frame_image)
        scroll_area = qt.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.settings_panel)
        setting_layout.addWidget(scroll_area)
        self.settings_panel.sigParametersChanged.connect(self.display_frame_image)

        segmentProgressOverWriteLayout = qt.QFormLayout()
        self._overwrite = qt.QCheckBox()
        self._progress_bar = qt.QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        segmentProgressOverWriteLayout.addRow(
            "Overwrite Segmentation Result", self._overwrite
        )
        segmentProgressOverWriteLayout.addRow(self._progress_bar)
        setting_layout.addLayout(segmentProgressOverWriteLayout)

        btn_layout = qt.QHBoxLayout()
        self._seg_scan_execute_btn = qt.QPushButton("Execute Segment Scan")
        self._seg_scan_execute_btn.clicked.connect(self._on_execute_segment)
        self._seg_scan_execute_btn.setSizePolicy(
            qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed
        )
        btn_layout.addWidget(self._seg_scan_execute_btn)
        self._segmenter_plot_btn = qt.QPushButton(qtawesome.icon("fa6.eye"), None)
        self._segmenter_plot_btn.setFlat(True)
        self._segmenter_plot_btn.setToolTip("Show 3D segmented result")
        self._segmenter_plot_btn.clicked.connect(self._plot_segmented_output)
        self._segmenter_plot_btn.setDisabled(True)
        self._segmenter_plot_btn.setSizePolicy(
            qt.QSizePolicy.Fixed, qt.QSizePolicy.Preferred
        )
        btn_layout.addWidget(self._segmenter_plot_btn)
        setting_layout.addLayout(btn_layout)

        self._last_params = None

        self.dual_plot_widget = SilxSyncDualPlot(self)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.settings_panel_widget)
        self.splitter.addWidget(self.dual_plot_widget)
        self.splitter.setSizes([300, 700])  # Adjust default widths

        self.mainArea.layout().addWidget(self.splitter)
        self.settings_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.dual_plot_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.mainArea.layout().addWidget(self.splitter)
        self.display_frame_image(None)

    def display_frame_image(self, params: dict | None):
        if not params:
            return

        raw_image, frame_idx, scale_factor = self.raw_image_frame(params)
        smoothed_img, peak_pos = segment_frame(raw_image, params, scale_factor)

        self.dual_plot_widget.setRightImage(
            array2D=smoothed_img,
            title=f"Background Corrected Image (Frame Idx {frame_idx})",
            xLabel="f_raw",
            yLabel="s_raw",
        )
        self.dual_plot_widget.setLeftImage(
            array2D=raw_image,
            title=f"Segmented #{len(peak_pos[0])}Peaks (Frame Idx {frame_idx})",
            xLabel="f_raw",
            yLabel="s_raw",
        )
        self.dual_plot_widget.setRightScatter(
            x=peak_pos[0],
            y=peak_pos[1],
            colormap=Colormap(name="grey_r"),
            symbol="d",
        )

    def raw_image_frame(self, params: dict) -> tuple[np.ndarray, int | None]:
        masterfile_path = Path(self.settings_panel.getMasterFilePath())
        frame_idx = self.settings_panel.getFrameIdx()
        raw_image = get_frame_image(
            file_path=masterfile_path,
            detector=params["file_folders"]["detector"],
            scan_id=str(self.settings_panel.getScanNumber()) + ".1",
            frame_idx=frame_idx,
        ).astype("uint16")
        if params["monitor_name"] is None:
            scale_factor = None
        else:
            scale_factor = get_monitor_scale_factor_for_frame_index(
                masterfile_path=masterfile_path,
                scan_number=str(self.settings_panel.getScanNumber()),
                detector=params["file_folders"]["detector"],
                monitor_name=params["monitor_name"],
                frame_idx=frame_idx,
            )
        return raw_image, frame_idx, scale_factor

    def _getParameters(self):
        params = self.settings_panel.getParameters()
        params = {
            **params,
            "overwrite": self._overwrite.isChecked(),
        }
        return params

    def _on_execute_segment(self):
        params = self._getParameters()
        if params == self._last_params:
            decision = ask_confirmation_to_repeat_segmentation()
            if decision == "cancel":
                return
            elif decision == "show":
                self._plot_segmented_output()
                return
            elif decision == "continue":
                pass
            else:
                raise ValueError(f"Unknown decision {decision}")

        self._disable_ui(True)
        self.set_dynamic_input("monitor_name", params["monitor_name"])
        self.set_dynamic_input("overwrite", params["overwrite"])
        self.set_dynamic_input("folder_config", params["file_folders"])
        self.set_dynamic_input("segmenter_algo_params", params["segmenter_config"])
        self.set_dynamic_input("correction_files", params["correction_files"])
        self.execute_ewoks_task()

    def task_output_changed(self):
        self._disable_ui(False)
        if self.task_exception:
            self._show_error(message=f"{self.task_exception}")
            return
        self._segmenter_plot_btn.setEnabled(True)
        self._last_params = self._getParameters()
        self._plot_segmented_output()
        self.progressBarSet(100)
        return super().task_output_changed()

    def _plot_segmented_output(self):
        outputs = self.get_task_output_values()
        data_url = DataUrl(outputs["segmented_peaks_url"])
        nexus_file_path = data_url.file_path()
        segmented_data_group_path = data_url.data_path()

        segmented_3d_peaks = read_peaks_attributes(
            filename=nexus_file_path,
            process_group=segmented_data_group_path,
        )
        plot = Ewoks3DXRDPlot2D()
        plot.addScatter(
            x=segmented_3d_peaks["f_raw"],
            y=segmented_3d_peaks["s_raw"],
            value=np.ones(len(segmented_3d_peaks["f_raw"])),
            legend="3D Segmented Peaks",
            symbol="+",
        )
        plot.setGraphXLabel("f_raw")
        plot.setGraphYLabel("s_raw")
        plot.setGraphTitle("3D Segmented Peaks")
        plot.resetZoom()
        plot.show()

    def progressBarSet(self, value: int):
        self._progress_bar.setValue(int(math.ceil(value)))

    def progressBarInit(self):
        self._progress_bar.setValue(0)

    def _disable_ui(self, disable: bool):
        widgets = [
            self._seg_scan_execute_btn,
            self.settings_panel,
        ]
        for w in widgets:
            w.setDisabled(disable)

    def _show_error(self, message: str):
        return qt.QMessageBox.critical(self, "Segmentation Error", message)

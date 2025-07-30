from __future__ import annotations

import os

from silx.gui import qt


class GeometryParameterGroupBox(qt.QGroupBox):

    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__("Geometry Settings", parent=parent, **kwargs)
        parmLayout = qt.QFormLayout(self)

        self._chi = qt.QLineEdit()
        self._distance = qt.QLineEdit()
        self._fit_tol = qt.QLineEdit()
        self._fit_tolerance = qt.QLineEdit()
        self._min_bin_prob = qt.QLineEdit()
        self._no_bins = qt.QLineEdit()
        self._o11 = qt.QLineEdit()
        self._o12 = qt.QLineEdit()
        self._o21 = qt.QLineEdit()
        self._o22 = qt.QLineEdit()
        self._omegasign = qt.QLineEdit()
        self._t_x = qt.QLineEdit()
        self._t_y = qt.QLineEdit()
        self._t_z = qt.QLineEdit()
        self._tilt_x = qt.QLineEdit()
        self._tilt_y = qt.QLineEdit()
        self._tilt_z = qt.QLineEdit()
        self._wavelength = qt.QLineEdit()
        self._wedge = qt.QLineEdit()
        self._weight_hist_intensities = qt.QLineEdit()
        self._y_center = qt.QLineEdit()
        self._y_size = qt.QLineEdit()
        self._z_center = qt.QLineEdit()
        self._z_size = qt.QLineEdit()

        parmLayout.addRow("chi", self._chi)
        parmLayout.addRow("distance", self._distance)
        parmLayout.addRow("fit_tol", self._fit_tol)
        parmLayout.addRow("fit_tolerance", self._fit_tolerance)
        parmLayout.addRow("min_bin_prob", self._min_bin_prob)
        parmLayout.addRow("no_bins", self._no_bins)
        parmLayout.addRow("o11", self._o11)
        parmLayout.addRow("o12", self._o12)
        parmLayout.addRow("o21", self._o21)
        parmLayout.addRow("o22", self._o22)
        parmLayout.addRow("omegasign", self._omegasign)
        parmLayout.addRow("t_x", self._t_x)
        parmLayout.addRow("t_y", self._t_y)
        parmLayout.addRow("t_z", self._t_z)
        parmLayout.addRow("tilt_x", self._tilt_x)
        parmLayout.addRow("tilt_y", self._tilt_y)
        parmLayout.addRow("tilt_z", self._tilt_z)
        parmLayout.addRow("wavelength", self._wavelength)
        parmLayout.addRow("wedge", self._wedge)
        parmLayout.addRow("weight_hist_intensities", self._weight_hist_intensities)
        parmLayout.addRow("y_center", self._y_center)
        parmLayout.addRow("y_size", self._y_size)
        parmLayout.addRow("z_center", self._z_center)
        parmLayout.addRow("z_size", self._z_size)

    def getGeometryParameterAsParFile(self, filePath: str):
        key_to_widget = {
            "chi": self._chi,
            "distance": self._distance,
            "fit_tol": self._fit_tol,
            "fit_tolerance": self._fit_tolerance,
            "min_bin_prob": self._min_bin_prob,
            "no_bins": self._no_bins,
            "o11": self._o11,
            "o12": self._o12,
            "o21": self._o21,
            "o22": self._o22,
            "omegasign": self._omegasign,
            "t_x": self._t_x,
            "t_y": self._t_y,
            "t_z": self._t_z,
            "tilt_x": self._tilt_x,
            "tilt_y": self._tilt_y,
            "tilt_z": self._tilt_z,
            "wavelength": self._wavelength,
            "wedge": self._wedge,
            "weight_hist_intensities": self._weight_hist_intensities,
            "y_center": self._y_center,
            "y_size": self._y_size,
            "z_center": self._z_center,
            "z_size": self._z_size,
        }

        parameters = {
            key: widget.text().strip()
            for key, widget in key_to_widget.items()
            if widget.text().strip() != ""
        }

        if not parameters:
            qt.QMessageBox.warning(
                self, "No Parameters", "No geometry parameters to write."
            )
            return None

        with open(filePath, "w") as f:
            for key, value in parameters.items():
                f.write(f"{key} {value}\n")

    def fillGeometryValues(self, filePath: str):
        if not os.path.exists(filePath):
            qt.QMessageBox.critical(
                self, "File Not Found", f"File does not exist:\n{filePath}"
            )
            return

        if not filePath.lower().endswith(".par"):
            qt.QMessageBox.warning(
                self, "Invalid File", "Selected file must end with `.par`."
            )
            return
        self._parse_par_file(filePath)

    def _parse_par_file(self, filePath: str):
        key_to_widget = {
            "chi": self._chi,
            "distance": self._distance,
            "fit_tol": self._fit_tol,
            "fit_tolerance": self._fit_tolerance,
            "min_bin_prob": self._min_bin_prob,
            "no_bins": self._no_bins,
            "o11": self._o11,
            "o12": self._o12,
            "o21": self._o21,
            "o22": self._o22,
            "omegasign": self._omegasign,
            "t_x": self._t_x,
            "t_y": self._t_y,
            "t_z": self._t_z,
            "tilt_x": self._tilt_x,
            "tilt_y": self._tilt_y,
            "tilt_z": self._tilt_z,
            "wavelength": self._wavelength,
            "wedge": self._wedge,
            "weight_hist_intensities": self._weight_hist_intensities,
            "y_center": self._y_center,
            "y_size": self._y_size,
            "z_center": self._z_center,
            "z_size": self._z_size,
        }

        with open(filePath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                key, value = map(str.strip, line.split(" ", 1))
                if key in key_to_widget:
                    key_to_widget[key].setText(value)

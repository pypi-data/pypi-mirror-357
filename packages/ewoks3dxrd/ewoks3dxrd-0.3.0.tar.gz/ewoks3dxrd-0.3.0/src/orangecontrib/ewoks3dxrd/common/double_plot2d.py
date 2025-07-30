from __future__ import annotations
from silx.gui import qt
from silx.gui.plot.utils.axis import SyncAxes
from silx.gui.colors import Colormap
from silx.gui.dialog.ColormapDialog import ColormapDialog
import numpy as np
from .utils import Ewoks3DXRDPlot2D


class DoublePlot2D(qt.QWidget):

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._left_plot = Ewoks3DXRDPlot2D(self)
        self._right_plot = Ewoks3DXRDPlot2D(self)

        self._x_axis_sync = SyncAxes(
            (self._left_plot.getXAxis(), self._right_plot.getXAxis())
        )
        self.y_axis_sync = SyncAxes(
            (self._left_plot.getYAxis(), self._right_plot.getYAxis())
        )

        self.colormap_dialog = ColormapDialog(parent=self)
        self.cmap = Colormap(
            name="viridis", normalization="log", autoscaleMode="percentile_1_99"
        )
        for plot in (self._left_plot, self._right_plot):
            plot.getColormapAction().setColormapDialog(self.colormap_dialog)
            plot.setDefaultColormap(self.cmap)

        self._left_plot.setAxesDisplayed(True)
        self._right_plot.setAxesDisplayed(True)

        layout = qt.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._left_plot)
        layout.addWidget(self._right_plot)
        self.setLayout(layout)

    def addLeftScatter(
        self, x: np.ndarray, y: np.ndarray, xlabel: str, ylabel: str, title: str
    ):
        self._left_plot.addScatter(
            x=x,
            y=y,
            value=np.ones(len(x)),
            symbol="+",
        )
        self._left_plot.setGraphXLabel(xlabel)
        self._left_plot.setGraphYLabel(ylabel)
        self._left_plot.setGraphTitle(title)
        self._left_plot.resetZoom()

    def addRightScatter(
        self, x: np.ndarray, y: np.ndarray, xlabel: str, ylabel: str, title: str
    ):
        self._right_plot.addScatter(
            x=x,
            y=y,
            value=np.ones(len(x)),
            symbol="+",
        )
        self._right_plot.setGraphXLabel(xlabel)
        self._right_plot.setGraphYLabel(ylabel)
        self._right_plot.setGraphTitle(title)
        self._right_plot.resetZoom()

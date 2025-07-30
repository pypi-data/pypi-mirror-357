from __future__ import annotations
from silx.gui import qt
from silx.gui.plot import Plot2D
import numpy as np


class Ewoks3DXRDPlot2D(Plot2D):
    def __init__(self, parent: qt.QWidget | None = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self.setBackgroundColor("white")
        self.setKeepDataAspectRatio(True)
        self.setAxesMargins(0.06, 0.06, 0.06, 0.06)
        self.setGraphGrid(True)
        self.setInteractiveMode(mode="pan")
        self.setBackend(backend="gl")


def add_image_to_plot(
    plot_wd: Ewoks3DXRDPlot2D,
    array_2d: np.ndarray,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    plot_wd.clear()
    plot_wd.setGraphTitle(title)
    plot_wd.addImage(
        array_2d,
        legend=title,
    )
    plot_wd.setGraphXLabel(label=x_label)
    plot_wd.setGraphYLabel(label=y_label)

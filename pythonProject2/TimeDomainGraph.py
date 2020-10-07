from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y1 = [randint(0, 100) for _ in range(100)]
        self.y2 = [randint(0, 50) for _ in range(100)]
        # Add Background colour to white
        self.graphWidget.setBackground('#ddd')
        # Add Title
        self.graphWidget.setTitle("Your Title Here", color="b", size="30pt")
        # Add Axis Labels
        styles = {"color": "#000", "font-size": "30px"}
        self.graphWidget.setLabel("left", "Temperature (°C)", **styles)
        self.graphWidget.setLabel("bottom", "Hour (H)", **styles)
        # Add legend
        self.graphWidget.addLegend(offset=(-1, 1))

        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        # Set Range
        self.graphWidget.setXRange(0, 10, padding=0)
        self.graphWidget.setYRange(20, 55, padding=0)

        self.data_line1 = self.graphWidget.plot(self.x, self.y1, "Sensor1", 'r')
        self.data_line2 = self.graphWidget.plot(self.x, self.y2, "Sensor2", 'b')
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y1 = self.y1[1:]  # Remove the first
        self.y1.append(randint(0, 100))  # Add a new random value.
        self.y2 = self.y2[1:]
        self.y2.append(randint(0, 50))
        self.data_line1.setData(self.x, self.y1)
        self.data_line2.setData(self.x,self.y2)

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=plotname, pen=pen, symbolSize=5, symbolBrush=(color))





import sys

import TimeDomainGraph


def main():
    app = TimeDomainGraph.QtWidgets.QApplication(sys.argv)
    graph = TimeDomainGraph.MainWindow()
    graph.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
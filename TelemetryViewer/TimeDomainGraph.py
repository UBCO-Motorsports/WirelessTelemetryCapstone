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
        self.graphWidget.showGrid(x=True, y=True)
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(200))  # 100 time points
        self.y = [randint(0,100) for _ in range(200)]  # 100 data points
        self.z = [randint(0, 100) for _ in range(200)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line1 =  self.graphWidget.plot(self.x, self.y,pen=(0,0,0))

        self.data_line2 = self.graphWidget.plot(self.x, self.z,pen=(255,0,0))

        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.
        self.z = self.z[1:]  # Remove the first
        self.z.append(randint(0, 100))  # Add a new random value.
        self.data_line1.setData(self.x, self.y)  # Update the data.
        self.data_line2.setData(self.x, self.z)  # Update the data.
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
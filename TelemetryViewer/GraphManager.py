import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import sys

from PyQt5.QtWidgets import QSplitter


class GraphManager(QtGui.QWidget):

    def __init__(self):
        super(GraphManager, self).__init__()

        self.graph_layout = QtGui.QGridLayout()
        self.setLayout(self.graph_layout)

        # Generates array of graphs and puts them in a layout
        # [Row][Column] to align with QGridLayout
        self.graph_array = [[],[],[],[]]
        for i in range(4):
            for j in range(4):
                self.graph_array[i].append(pg.PlotWidget())
                self.graph_layout.addWidget(self.graph_array[i][j], i, j)
                self.graph_array[i][j].showGrid(x=True, y=True)
                self.graph_array[i][j].setBackground('w')

    def graphSelect(self):
        return
        #TODO

    def showGraphs(self, num_shown):
        # Reset formats to better align widgets
        for i in range(4):
            self.graph_layout.setColumnStretch(i, 0)
            self.graph_layout.setRowStretch(i, 0)

        if num_shown == '1':
            for i in range(1, 4):
                self.graph_array[0][i].hide()
            for i in range(1, 4):
                for j in range(4):
                    self.graph_array[i][j].hide()

        elif num_shown == '2':
            self.graph_array[1][0].show()
            for i in range(2):
                for j in range(1, 4):
                    self.graph_array[i][j].hide()
            for i in range(2, 4):
                for j in range(4):
                    self.graph_array[i][j].hide()
            self.graph_array[0][0].resize(self.width(), self.height()/2)
            self.graph_array[1][0].resize(self.width(), self.height()/2)

        elif num_shown == '4':
            for i in range(2):
                for j in range(2):
                    self.graph_array[i][j].show()
            for i in range(2):
                for j in range(2, 4):
                    self.graph_array[i][j].hide()
            for i in range(2, 4):
                for j in range(4):
                    self.graph_array[i][j].hide()
            self.graph_array[0][0].resize(self.width()/2, self.height()/2)
            self.graph_array[1][0].resize(self.width()/2, self.height()/2)
            self.graph_array[0][1].resize(self.width()/2, self.height()/2)
            self.graph_array[1][1].resize(self.width()/2, self.height()/2)

        elif num_shown == '8':
            for i in range(2,4):
                for j in range(4):
                    self.graph_array[i][j].hide()
            for i in range(2):
                for j in range(4):
                    self.graph_array[i][j].show()

            for i in range(2):
                for j in range(4):
                    self.graph_array[i][j].setGeometry(j * self.width()/4, i * self.height()/2, self.width()/4, self.height()/2)
                    print(self.graph_array[i][j].frameGeometry())

        elif num_shown == '16':
            for i in range(4):
                # Reformats layout of widgets
                self.graph_layout.setColumnStretch(i, 1)
                self.graph_layout.setRowStretch(i, 1)
                for j in range(4):
                    self.graph_array[i][j].show()


# app = QtWidgets.QApplication(sys.argv)
# test = GraphManager()
# test.show()
# app.setAttribute(QtCore.Qt.AA_Use96Dpi)
# sys.exit(app.exec_())
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from RPM import RPMGauge
from Speedo import splashScreen

from PyQt5.QtWidgets import QSplitter
from Serial import SerialModule     #dont comment or delete > needed for Serial communication


class GraphManager(QtGui.QWidget):

    def __init__(self, parentwidget):
        super(GraphManager, self).__init__(parentwidget)
        self.parentwidget = parentwidget
        self.SerialModule = SerialModule()
        # self.SerialModule.connectSerial()

        self.graph_layout = QtGui.QGridLayout()
        self.setLayout(self.graph_layout)

        self.r = 255
        self.g = 0
        self.b = 0
        self.pen = pg.mkPen(color=(self.r,self.g,self.b),width=2)

        # Generate test data
        self.x = [i for i in range(200)]
        self.y = [i for i in range(200)]
        self.z = [-i for i in range(200)]

        # Generates array of graphs and puts them in a layout
        # [Row][Column] to align with QGridLayout
        self.graph_array = [[],[],[]]
        for i in range(3):
            for j in range(4):
                self.graph_array[i].append(PlotWdgt(self))
                current_graph = self.graph_array[i][j]
                self.graph_layout.addWidget(current_graph, i, j)
                current_graph.showGrid(x=True, y=True)

                current_graph.xData = self.x
                current_graph.yData = self.SerialModule.array1

                plotItem = current_graph.getPlotItem()
                plotItem.setLabels(top=self.graph_array[i][j].title, bottom=current_graph.xLabel)
                # plotItem.setLabel('top', text=self.graph_array[i][j].title)
                # plotItem.setLabel('bottom', text=self.graph_array[i][j].xLabel)
                plotItem.setLabel('left', text=self.graph_array[i][j].yLabel)

        # self.graph_array[0][0].xData.append(self.x)
        # self.graph_array[0][0].yData.append(self.SerialModule.array1)
        #
        # self.dial = RPMGauge()
        # self.graph_array[0][0].hide()
        # self.graph_layout.removeWidget (self.graph_array[0][0])
        # self.graph_array[0][0].close()
        # self.graph_array[0][0] = self.dial
        # self.graph_layout.addWidget(self.dial, 0, 0)
        # self.dial.dial_size.setGeometry(-10,-10,320,320)

        # self.speedo = splashScreen(self)
        # self.speed = 0
        # # self.speedo.raise_()
        # self.graph_layout.removeWidget(self.graph_array[0][1])
        # self.graph_array[0][1].close()
        # self.graph_array[0][1] = self.speedo
        # self.graph_layout.addWidget(self.speedo, 0, 1)
        # # self.speedo.frame_size.setGeometry(-10,-10,320,320)

    #TODO
    def updateWidget(self, current_widget, applied_type):
        if current_widget.type != applied_type:
            position = self.findWidgetPosition(current_widget)
            if applied_type == 'Time Domain':
                new_widget = PlotWdgt(self)
            elif applied_type == 'Polar Plot':
                new_widget = PlotWdgt(self) #TODO make polarplot widget
                new_widget.type = 'Polar Plot'
            elif applied_type == 'RPM Gauge':
                new_widget = RPMGauge(self)
            elif applied_type == 'Speedo Gauge':
                new_widget = splashScreen(self)
            else:
                print('widget update failed')
                pass
            self.graph_array[position[0]][position[1]] = new_widget
            self.graph_layout.replaceWidget(current_widget, self.graph_array[position[0]][position[1]])
            current_widget.close()
        else:
            new_widget = current_widget
        return new_widget

    def findWidgetPosition(self, current_widget):
        for i, row in enumerate(self.graph_array):
            for j, widget in enumerate(row):
                if widget == current_widget:
                    return (i, j) # row,column
        print("Couldn't find widget in layout: see findWidgetPostition")

    def configMenuCalled(self, plotWidget):
        self.current_widget = plotWidget
        self.parentwidget.configMenuCalled(plotWidget)

    def update(self):
        #TODO
        # Call update for element in graph_array, if graph_array[i][j] == [polar]: update_polar()
        # Graph -> Update Graph, Dial -> Update Dial, Polar -> Update Polar

        # Update test data
        del self.x[0]  # Remove the first x element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        del self.y[0]
        self.y.append(self.y[-1] + 1)
        del self.z[0]
        self.z.append(self.z[-1] - 1)

        # Read latest data if serial is connected
        if self.parentwidget.serialConnected:
            self.SerialModule.readSerial()

            # Gets a sample of the latest arrays
            self.serialArrays = self.SerialModule.getData()
            dialtest = self.serialArrays[2]
            self.speedo.Speed = dialtest[-1]

            # Iterates through each graph/dial and refreshes its data
            for i, row in enumerate(self.graph_array):
                for graph in row:
                    if graph.type == 'Time Domain':
                        graph.clear()
                        graph.plot(graph.xData, self.serialArrays[i], pen=self.pen, clear=True)
                        # print('cartesian')
                    elif graph.type == 'Speedo Gauge':
                        if graph.Speed < 150:
                            print('increase')
                            graph.animate(graph.Speed)
                            graph.Speed += 1
                        else:
                            print('set zero')
                            self.speedo.Speed = 0
                    elif graph.type == 'Polar Plot':
                        pass
                        # print('polar')

    def showGraphs(self, num_shown):
        if num_shown == '12':
            for row in range(len(self.graph_array)):
                for column in range(len(self.graph_array[row])):
                    self.graph_array[row][column].show()
        elif num_shown == '8':
            self.showGraphs('12')
            for column in range(len(self.graph_array[2])):
                self.graph_array[2][column].hide()
        elif num_shown == '6':
            self.showGraphs('8')
            for row in range(2):
                self.graph_array[row][3].hide()
        elif num_shown == '4':
            self.showGraphs('6')
            for row in range(2):
                self.graph_array[row][2].hide()
        elif num_shown == '2':
            self.showGraphs('4')
            for row in range(2):
                self.graph_array[row][1].hide()
        elif num_shown == '1':
            self.showGraphs('2')
            self.graph_array[1][0].hide()

class PlotWdgt(pg.PlotWidget):
    def __init__(self, parentwidget, parent=None):
        super(PlotWdgt, self).__init__(parent, viewBox=CustomViewBox(self))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored))
        self.parentwidget = parentwidget
        self.plot_item = self.getPlotItem()
        self.plot_item.getAxis('top').setStyle(showValues=False)
        self.setBackground('w')

        self.legend = self.plot_item.addLegend()

        self.type = 'Time Domain'
        self.xData = []
        self.yData = []
        self.xLabel = 'X-Axis'
        self.yLabel = 'Y-Axis'
        self.title = 'X vs. Y'
        self.yRange = [0, 1]
        self.autoRange = True
        #TODO store the current axis labels, legend, and datasets to populate config menu

    def configMenuCalled(self):
        # Calls parent widget to open edit menu
        self.parentwidget.configMenuCalled(self)

class CustomViewBox(pg.ViewBox):
    def __init__(self, parentwidget, parent=None):
        super(CustomViewBox, self).__init__(parent)
        self.menu = pg.ViewBoxMenu.ViewBoxMenu(self)
        self.parentwidget = parentwidget

        # Adds edit option to right click menu
        self.menu.addSeparator()
        self.editData = QtGui.QAction("Edit Data", self.menu)
        self.editData.triggered.connect(self.parentwidget.configMenuCalled)
        self.menu.addAction(self.editData)

# app = QtWidgets.QApplication(sys.argv)
# test = GraphManager()
# test.show()
# app.setAttribute(QtCore.Qt.AA_Use96Dpi)
# sys.exit(app.exec_())
import pyqtgraph as pg
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from RPM import RPMGauge
from Speedo import splashScreen
from Serial import SerialModule     #dont comment or delete > needed for Serial communication


class GraphManager(QtGui.QWidget):

    def __init__(self, parentwidget):
        super(GraphManager, self).__init__(parentwidget)
        self.parentwidget = parentwidget
        self.SerialModule = SerialModule()

        self.graph_layout = QtGui.QGridLayout()
        self.setLayout(self.graph_layout)

        self.r = 255
        self.g = 0
        self.b = 0
        self.pen = pg.mkPen(color=(self.r,self.g,self.b),width=2)

        # Generate time array
        self.x = []

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

    def updateWidget(self, current_widget, applied_type):
        if current_widget.type != applied_type:
            position = self.findWidgetPosition(current_widget)
            if applied_type == 'Time Domain':
                new_widget = PlotWdgt(self)
                new_widget.xData = self.x
            elif applied_type == 'Polar Plot':
                new_widget = PolarWidget(self)
            elif applied_type == 'RPM Gauge':
                new_widget = RPMGauge(self)
                new_widget.ui.frame_3.setStyleSheet('border: 3px solid #00ff00;')
                new_widget.highlighted = True
            elif applied_type == 'Speedo Gauge':
                new_widget = splashScreen(self)
                new_widget.ui.frame_3.setStyleSheet('border: 3px solid #00ff00;')
                new_widget.highlighted = True
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
        # Update time data
        if len(self.x) >= 200: #TODO set buffer size
            del self.x[0]  # Remove the first x element.
        now = datetime.now()
        self.x.append(now.timestamp())

        # Read latest data if serial is connected
        if self.parentwidget.serialConnected:

            # Gets a sample of the latest arrays
            self.SerialModule.readSerial()
            self.serialArrays = self.SerialModule.getData()

            # Iterates through each graph/dial and refreshes its data
            for i, row in enumerate(self.graph_array):
                for graph in row:
                    # Checks widget type and updates it accordingly
                    if graph.type == 'Time Domain':
                        graph.clear()
                        if graph.yData:
                            for index in graph.yData:
                                try:
                                    colour = self.parentwidget.selected_channels["logged"][index]['Color']
                                    rgba = self.parentwidget.getColor(colour)
                                    pen = pg.mkPen(color=(rgba[0],rgba[1],rgba[2]),width=2)
                                except:
                                    pen = self.pen
                                # Match length of x and y arrays
                                ydata_len = len(self.serialArrays[index])
                                xdata_slice = len(graph.xData) - ydata_len
                                graph.plot(graph.xData[xdata_slice::], self.serialArrays[index], pen=pen)
                    elif graph.type == 'Polar Plot':
                        graph.clear()
                        if graph.yData and graph.xData:
                            try:
                                colour = self.parentwidget.selected_channels["logged"][graph.xData[0]]['Color']
                                rgba = self.parentwidget.getColor(colour)
                                pen = pg.mkPen(color=(rgba[0],rgba[1],rgba[2]),width=2)
                            except:
                                pen = self.pen
                            graph.plot(self.serialArrays[graph.xData[0]][-graph.samples:], self.serialArrays[graph.yData[0]][-graph.samples:], pen=pen)
                    elif graph.type == 'Speedo Gauge':
                        graph.animate(self.serialArrays[graph.yData[0]][-1])
                    elif graph.type == 'RPM Gauge':
                        graph.animate(self.serialArrays[graph.yData[0]][-1])
                        pass

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
    def __init__(self, parentwidget, parent=None, enabletime=True):
        if enabletime is True:
            timeaxisitem = {'bottom': TimeAxisItem('bottom')}
        else:
            timeaxisitem = None
        super(PlotWdgt, self).__init__(parent, axisItems=timeaxisitem, viewBox=CustomViewBox(self))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored))
        self.parentwidget = parentwidget
        self.plot_item = self.getPlotItem()
        self.plot_item.getAxis('top').setStyle(showValues=False)
        self.plot_item.showGrid(x=True, y=True)
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

        self.plot_item.setLabels(top=self.title, bottom=self.xLabel, left=self.yLabel)
        self.plot_item.getAxis('top').enableAutoSIPrefix(False)

    def configMenuCalled(self):
        # Calls parent widget to open edit menu
        self.parentwidget.configMenuCalled(self)

class PolarWidget(PlotWdgt):
    def __init__(self, parentwidget):
        super(PolarWidget, self).__init__(parentwidget, enabletime=False)
        self.type = 'Polar Plot'
        self.title = 'Polar Plot'
        self.xRange = [-10, 10]
        self.xAutoRange = False
        self.yRange = [-10, 10]
        self.yAutoRange = False
        self.samples = 3

        self.plot_item.setLabel('top', self.title)
        self.setXRange(self.xRange[0], self.xRange[1])
        self.setYRange(self.yRange[0], self.yRange[1])

class TimeAxisItem(pg.AxisItem):
    def __init__(self, placement):
        super(TimeAxisItem, self).__init__(placement)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [str(datetime.fromtimestamp(value).strftime('%H:%M:%S')) for value in values]

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
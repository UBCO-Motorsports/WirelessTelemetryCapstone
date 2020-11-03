from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QDockWidget, QAction, QMenu, QVBoxLayout, QTextEdit, QStackedWidget, QListWidget, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import numpy as np
from Loader import SplashScreen

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Init widgets/menus
        self.initToolbar()
        self.initMenuBar()
        self.initDockButtons()

        self.statusBar().showMessage('Ready')

        # List widget to store the display widgets
        self.widgetList = QListWidget()
        self.widgetList.insertItem(0, 'Home')
        self.widgetList.insertItem(1, 'Graph')

        # Init stack widget and add widgets to it
        self.Stack = QStackedWidget(self)
        self.mainWidget = QtGui.QWidget()
        self.homeWidget = QtGui.QWidget()
        self.Stack.addWidget(self.homeWidget)
        self.Stack.addWidget(self.mainWidget)

        # Main window set up
        self.setWindowTitle('Capstone Telemetry')
        self.setCentralWidget(self.Stack)

        # Layouts for display widgets
        self.homeLayout = QtGui.QGridLayout()
        self.homeWidget.setLayout(self.homeLayout)

        self.graphLayout = QtGui.QGridLayout()
        self.mainWidget.setLayout(self.graphLayout)

        # Init home widget
        self.homeText = QLabel()
        self.homeText.setText("Welcome to the Telemetry Viewer")
        self.homeText.setAlignment(Qt.AlignCenter)
        self.homeFont = QFont('Monospace', 20, QFont.Bold)
        self.homeText.setFont(self.homeFont)
        self.homeLayout.addWidget(self.homeText)

        self.homePicture = QtGui.QLabel(self)
        self.homePicture.setPixmap(QtGui.QPixmap("TelemetryLogo.png"))
        self.homeLayout.addWidget(self.homePicture, 1, 0, Qt.AlignCenter)

        # ---------------Testing plot stuff-----------------
        self.test_graph_widget = QtGui.QWidget()
        self.Stack.addWidget(self.test_graph_widget)
        self.test_graph_layout = QtGui.QGridLayout()
        self.test_graph_widget.setLayout(self.test_graph_layout)
        self.graph_list = []
        j = 0
        for i in range(16):
            self.graph_list.append(pg.PlotWidget())
            self.graph_list[i].showGrid(x=True, y=True)
            self.test_graph_layout.addWidget(self.graph_list[i], i%4, j)
            # self.test_graph_layout.setColumnStretch(j, 1)
            # self.test_graph_layout.setRowStretch(j, 1)
            if i%4 == 3:
                j+=1

        # Init plot widgets
        self.graphWidget = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget3 = pg.PlotWidget()
        self.graphWidget4 = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget2.showGrid(x=True, y=True)
        self.graphWidget3.showGrid(x=True, y=True)
        self.graphWidget4.showGrid(x=True, y=True)

        self.graphLayout.addWidget(self.graphWidget, 0, 0)
        self.graphLayout.addWidget(self.graphWidget2, 1, 0)
        self.graphLayout.addWidget(self.graphWidget3, 0, 1)
        self.graphLayout.addWidget(self.graphWidget4, 1, 1)

        self.graphWidget.setBackground('w')

        # Generate initial plot data
        self.x = list(range(200))  # 100 time points
        self.y = [randint(0,100) for _ in range(200)]  # 100 data points
        self.z = [randint(0, 100) for _ in range(200)]  # 100 data points
        self.sin = []
        for i in range(200):
            self.sin.append(np.sin(self.x[i]) + 50)

        self.pen = pg.mkPen(color=(255,0,0),width=2)

        # Initial plot
        self.data_line1 = self.graphWidget.plot(self.x, self.y,pen=self.pen)
        self.data_line2 = self.graphWidget2.plot(self.x, self.z,pen=pg.mkPen(color=(0,255,0),width=2))
        self.data_line3 = self.graphWidget3.plot(self.x, self.z,pen=pg.mkPen(color=(0,0,255),width=2))
        self.sinwave = self.graphWidget4.plot(self.x, self.sin, pen=pg.mkPen(color=(0,255,0),width=2))

        self.line_plots = []
        for i in self.graph_list:
            self.line_plots.append(i.plot(self.x, self.y,pen=self.pen))

        # Set refresh rate for graph
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def initDockButtons(self):
        # Init buttons
        # self.button = QtWidgets.QPushButton(self)
        # self.button.setText("Green")
        # self.button.clicked.connect(self.colour_green)
        #
        # self.button2 = QtWidgets.QPushButton(self)
        # self.button2.setText("Random Test")
        # self.button2.clicked.connect(self.sineoff)
        #
        # self.button3 = QtWidgets.QPushButton(self)
        # self.button3.setText("Sine Test")
        # self.button3.clicked.connect(self.sineon)

        # Init number of graph selection menu
        self.numGraphs = QtGui.QWidget()
        self.numGraphsLayout = QtGui.QVBoxLayout()

        self.numGraphLabel = QLabel('Select # of Graphs')
        self.numGraphLabel.setFixedHeight(20)
        self.comboBox = QComboBox()
        self.comboBox.setToolTip('# of Graphs')
        self.comboBox.addItem('1')
        self.comboBox.addItem('2')
        self.comboBox.addItem('4')
        self.comboBox.addItem('16')
        self.comboBox.setCurrentIndex(2)
        self.comboBox.currentIndexChanged.connect(self.graphshift)

        self.numGraphsLayout.addWidget(self.numGraphLabel)
        self.numGraphsLayout.addWidget(self.comboBox)
        self.numGraphs.setLayout(self.numGraphsLayout)

        # Init display list
        # self.data_selection_widget = QtGui.QWidget()
        self.data_selection_box = QComboBox()
        self.data_selection_box.setToolTip('Graph selection')
        for i in range(4):
            for j in range(4):
                self.data_selection_box.addItem('(%s, %s)' % (str(i), str(j)))
        self.numGraphsLayout.addWidget(self.data_selection_box)

        self.plot_selection_box = QComboBox()
        self.plot_selection_box.setToolTip('Which data to show')
        self.plot_selection_box.addItem('Y')
        self.plot_selection_box.addItem('Z')
        self.numGraphsLayout.addWidget(self.plot_selection_box)

        # Place buttons in dock widget section
        self.dock = QDockWidget("Graph Options", self)
        self.buttons = QtGui.QWidget() # Set up widget to put buttons in
        self.btn_layout = QtGui.QVBoxLayout() # Layout for buttons
        # self.btn_layout.addWidget(self.button)
        # self.btn_layout.addWidget(self.button2)
        # self.btn_layout.addWidget(self.button3)
        self.btn_layout.addWidget(self.numGraphs)
        self.buttons.setLayout(self.btn_layout) # Apply button layout to button widget
        self.dock.setWidget(self.buttons) # Set dock widget to contain buttons
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock) # Place button dock widget in window
        self.dock.setFloating(False)
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock.hide() # Hide dock widget from home screen

    def initToolbar(self):
        # Init actions to add to toolbar
        self.toolHome = QAction(QIcon('icons/home.png'), 'Home', self)
        self.toolHome.setStatusTip('Home')
        self.toolHome.setCheckable(True)
        self.toolHome.setChecked(True)
        self.toolHome.triggered.connect(self.displayHome)

        self.toolGraph = QAction(QIcon('icons/graphic-card.png'), 'Graph', self)
        self.toolGraph.setStatusTip('Graphs')
        self.toolGraph.setCheckable(True)
        self.toolGraph.triggered.connect(self.displayGraph)

        self.toolTestGraph = QAction(QIcon('icons/graphic-card.png'), 'Graph', self)
        self.toolTestGraph.setStatusTip('Graphs')
        self.toolTestGraph.setCheckable(True)
        self.toolTestGraph.triggered.connect(self.displayTestGraph)

        # Add toolbar to left side
        self.toolbar = QtWidgets.QToolBar('Red')
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

        self.toolbar.addAction(self.toolHome)
        self.toolbar.addAction(self.toolGraph)
        self.toolbar.addAction(self.toolTestGraph)


    def initMenuBar(self):
        # Init a menu bar
        menubar = self.menuBar()

        #Menu options
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')

        # Set actions for each menu-----------------------------
        # Home menu
        homeAction = QAction('Home Page', self)
        homeAction.triggered.connect(self.displayHome)
        fileMenu.addAction(homeAction)

        data_log_action = QAction('--Log Data', self)
        data_log_action.setCheckable(True)
        fileMenu.addAction(data_log_action)
        # Need to add trigger function for data logging
        # data_log_action.triggered.connect(dataloggingon)

        com_menu = QMenu('--Select COM', self)
        com_options = QActionGroup(com_menu)
        com_ports = ["COM1", "COM2", "COM3", "COM4"]
        for port in com_ports:
            com_action = QAction(port, com_menu, checkable=True, checked=port==[0])
            com_menu.addAction(com_action)
            com_options.addAction(com_action)
        com_options.setExclusive(True)
        # Trigger COM port swap
        # com_options.triggered.connect()
        fileMenu.addMenu(com_menu)

        # Edit menu
        newAct = QAction('Aqua', self)
        newAct.triggered.connect(self.colour_aqua)
        newAction = QAction('Blue', self)
        newAction.triggered.connect(self.colour_blue)
        editMenu.addAction(newAct)
        editMenu.addAction(newAction)
        # --------------------------------------------------------

    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.
        self.z = self.z[1:]  # Remove the first
        self.z.append(randint(0, 100))  # Add a new random value.
        self.sin = self.sin[1:]
        self.sin.append(np.sin(self.x[-1]) + 50)
        self.data_line1.setData(self.x, self.y)  # Update the data.
        self.data_line2.setData(self.x, self.z)  # Update the data.
        self.data_line3.setData(self.x, self.z)  # Update the data.
        self.sinwave.setData(self.x, self.sin)

        for i in self.line_plots:
            i.setData(self.x, self.y)

    def graphshift(self):
        if self.comboBox.currentText() == '1':
            for i in range(15):
                self.graph_list[i].hide()
                self.test_graph_layout.setColumnStretch(i, 0)
                self.test_graph_layout.setRowStretch(i, 0)
            self.graphWidget2.hide()
            self.graphWidget3.hide()
            self.graphWidget4.hide()

        elif self.comboBox.currentText() == '2':
            for i in range(14):
                self.graph_list[i].hide()
                self.test_graph_layout.setRowStretch(i, 0)
                self.test_graph_layout.setColumnStretch(i, 0)
            self.graph_list[14].show()
            self.graphWidget2.show()
            self.graphWidget3.hide()
            self.graphWidget4.hide()

        elif self.comboBox.currentText() == '4':
            for i in range(14, 11, -1):
                self.graph_list[i].show()
            for i in range(12):
                self.graph_list[i].hide()
                self.test_graph_layout.setRowStretch(i, 0)
                self.test_graph_layout.setColumnStretch(i, 0)
            self.graphWidget2.show()
            self.graphWidget3.show()
            self.graphWidget4.show()

        elif self.comboBox.currentText() == '16':
            self.graphWidget2.show()
            self.graphWidget3.show()
            self.graphWidget4.show()
            for j in range(4):
                self.test_graph_layout.setColumnStretch(j, 1)
                self.test_graph_layout.setRowStretch(j, 1)
            for i in self.graph_list:
                i.show()

    def colour_green(self):
        self.data_line1.setData(pen = pg.mkPen(color=(0,255,0),width=2))

    def colour_aqua(self):
        self.data_line1.setData(pen = pg.mkPen(color=(0,255,255),width=2))

    def colour_red(self):
        self.data_line1.setData(pen=pg.mkPen(color=(255, 0, 0), width=2))

    def colour_blue(self):
        self.data_line1.setData(pen=pg.mkPen(color=(0, 0, 255), width=2))

    def sineoff(self):
        self.graphWidget4.addItem(self.data_line3)
        self.graphWidget3.addItem(self.sinwave)

    def sineon(self):
        self.graphWidget4.addItem(self.sinwave)
        self.graphWidget3.addItem(self.data_line3)

    def displayHome(self):
        self.Stack.setCurrentIndex(0)
        self.dock.hide()
        self.toolHome.setChecked(True)
        self.toolGraph.setChecked(False)
        self.toolTestGraph.setChecked(False)

    def displayGraph(self):
        self.Stack.setCurrentIndex(1)
        self.dock.show()
        self.toolHome.setChecked(False)
        self.toolGraph.setChecked(True)
        self.toolTestGraph.setChecked(False)


    def displayTestGraph(self):
        self.Stack.setCurrentIndex(2)
        self.dock.show()
        self.toolHome.setChecked(False)
        self.toolGraph.setChecked(False)
        self.toolTestGraph.setChecked(True)

app = QtWidgets.QApplication(sys.argv)
l = SplashScreen()
l.show()
w = MainWindow()
w.show()
# Helps with window alignments
app.setAttribute(QtCore.Qt.AA_Use96Dpi)
sys.exit(app.exec_())
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
        self.homeText.setAlignment(Qt.AlignTop)
        self.homeFont = QFont('Monospace', 20, QFont.Bold)
        self.homeText.setFont(self.homeFont)
        self.homeLayout.addWidget(self.homeText)

        self.homeTextEdit = QTextEdit('Home')
        self.homeLayout.addWidget(self.homeTextEdit)

        # Init plot widgets
        self.graphWidget = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget2.hide()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget2.showGrid(x=True, y=True)

        self.graphLayout.addWidget(self.graphWidget, 0, 0)
        self.graphLayout.addWidget(self.graphWidget2, 1, 0)

        # Generate initial plot data
        self.x = list(range(200))  # 100 time points
        self.y = [randint(0,100) for _ in range(200)]  # 100 data points
        self.z = [randint(0, 100) for _ in range(200)]  # 100 data points
        self.sin = []
        for i in range(200):
            self.sin.append(20*np.sin(self.x[i]) + 50)

        self.graphWidget.setBackground('w')
        pen = pg.mkPen(color=(255,0,0),width=2)

        # Initial plot
        self.data_line1 = self.graphWidget.plot(self.x, self.y,pen=pen)
        self.data_line2 = self.graphWidget.plot(self.x, self.z,pen=pg.mkPen(color=(0,0,0),width=2))
        self.data_line3 = self.graphWidget2.plot(self.x, self.z,pen=pg.mkPen(color=(0,255,0),width=2))
        self.graphWidget2.removeItem(self.data_line3) # Janky method for testing plot swapping
        self.sinwave = self.graphWidget2.plot(self.x, self.sin, pen=pg.mkPen(color=(0,255,0),width=2))

        # Set refresh rate for graph
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def initDockButtons(self):
        # Init buttons
        self.button = QtWidgets.QPushButton(self)
        self.button.setText("Green")
        self.button.clicked.connect(self.colour_green)

        self.button2 = QtWidgets.QPushButton(self)
        self.button2.setText("Random")
        self.button2.clicked.connect(self.sineoff)

        self.button3 = QtWidgets.QPushButton(self)
        self.button3.setText("Sine")
        self.button3.clicked.connect(self.sineon)

        # Init selection menu
        self.numGraphs = QtGui.QWidget()
        self.numGraphsLayout = QtGui.QVBoxLayout()
        self.numGraphLabel = QLabel('Select # of Graphs')
        self.numGraphLabel.setFixedHeight(20)
        self.comboBox = QComboBox()
        self.comboBox.setToolTip('# of Graphs')
        self.comboBox.addItem('1')
        self.comboBox.addItem('2')
        self.comboBox.currentIndexChanged.connect(self.graphshift)

        self.numGraphsLayout.addWidget(self.numGraphLabel)
        self.numGraphsLayout.addWidget(self.comboBox)
        self.numGraphs.setLayout(self.numGraphsLayout)

        # Place buttons in dock widget section
        self.dock = QDockWidget("Dock", self)
        self.buttons = QtGui.QWidget() # Set up widget to put buttons in
        self.btn_layout = QtGui.QVBoxLayout() # Layout for buttons
        self.btn_layout.addWidget(self.button)
        self.btn_layout.addWidget(self.button2)
        self.btn_layout.addWidget(self.button3)
        self.btn_layout.addWidget(self.numGraphs)
        self.buttons.setLayout(self.btn_layout) # Apply button layout to button widget
        self.dock.setWidget(self.buttons) # Set dock widget to contain buttons
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock) # Place button dock widget in window
        self.dock.setFloating(False)
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

        # Add toolbar to left side
        self.toolbar = QtWidgets.QToolBar('Red')
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

        self.toolbar.addAction(self.toolHome)
        self.toolbar.addAction(self.toolGraph)

    def initMenuBar(self):
        # Init a menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')

        homeAction = QAction('Home Page', self)
        homeAction.triggered.connect(self.displayHome)
        fileMenu.addAction(homeAction)

        newAct = QAction('Aqua', self)
        newAct.triggered.connect(self.colour_aqua)
        newAction = QAction('Blue', self)
        newAction.triggered.connect(self.colour_blue)
        editMenu.addAction(newAct)
        editMenu.addAction(newAction)

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

    def graphshift(self):
        if self.comboBox.currentText() == '1':
            self.graphWidget2.hide()
        if self.comboBox.currentText() == '2':
            self.graphWidget2.show()

    def colour_green(self):
        self.data_line1.setData(pen = pg.mkPen(color=(0,255,0),width=2))

    def colour_aqua(self):
        self.data_line1.setData(pen = pg.mkPen(color=(0,255,255),width=2))

    def colour_red(self):
        self.data_line1.setData(pen=pg.mkPen(color=(255, 0, 0), width=2))

    def colour_blue(self):
        self.data_line1.setData(pen=pg.mkPen(color=(0, 0, 255), width=2))

    def sineoff(self):
        self.graphWidget2.removeItem(self.sinwave)
        self.graphWidget2.addItem(self.data_line3)

    def sineon(self):
        self.graphWidget2.addItem(self.sinwave)
        self.graphWidget2.removeItem(self.data_line3)

    def displayHome(self):
        self.Stack.setCurrentIndex(0)
        self.dock.hide()
        self.toolHome.setChecked(True)
        self.toolGraph.setChecked(False)

    def displayGraph(self):
        self.Stack.setCurrentIndex(1)
        self.dock.show()
        self.toolHome.setChecked(False)
        self.toolGraph.setChecked(True)



app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
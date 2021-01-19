from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QDockWidget, QAction, QMenu, QVBoxLayout, QTextEdit, QStackedWidget, QListWidget, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import numpy as np
from Loader import SplashScreen
from GraphManager import GraphManager


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Init widgets/menus
        self.initToolbar()
        self.initMenuBar()
        self.initDockButtons()

        self.statusBar().showMessage('Ready')

        # Init stack widget and add widgets to it
        self.Stack = QStackedWidget(self)
        self.homeWidget = QtGui.QWidget()
        self.Stack.addWidget(self.homeWidget)

        # Main window set up
        self.setWindowTitle('Capstone Telemetry')
        self.setCentralWidget(self.Stack)

        # Layouts for display widgets
        self.homeLayout = QtGui.QGridLayout()
        self.homeWidget.setLayout(self.homeLayout)

        # Init home widget
        self.homeText = QLabel()
        self.homeText.setText("Welcome to the Telemetry Viewer")
        self.homeText.setAlignment(Qt.AlignCenter)
        self.homeFont = QFont('Monospace', 20, QFont.Bold)
        self.homeText.setFont(self.homeFont)
        self.homeLayout.addWidget(self.homeText)

        self.homePicture = QtGui.QLabel(self)
        self.homePicture.setPixmap(QtGui.QPixmap("QT Images/TelemetryLogo.png"))
        self.homeLayout.addWidget(self.homePicture, 1, 0, Qt.AlignCenter)

        # Init graphs using graphing class
        self.GraphClass = GraphManager()
        self.Stack.addWidget(self.GraphClass)

        # Generate initial plot data
        self.x = list(range(200))  # 100 time points
        self.y = [randint(0,100) for _ in range(200)]  # 100 data points
        self.z = [randint(0, 100) for _ in range(200)]  # 100 data points
        self.sin = []
        for i in range(200):
            self.sin.append(np.sin(self.x[i]) + 50)

        self.pen = pg.mkPen(color=(255,0,0),width=2)

        # Generate graphs
        for row in self.GraphClass.graph_array:
            for graph in row:
                graph.plot(self.x, self.y, pen=self.pen)

        # Set refresh rate for graph
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def initDockButtons(self):

        # Init number of graph selection menu
        self.numGraphs = QtGui.QWidget()
        self.numGraphsLayout = QtGui.QVBoxLayout()

        self.numGraphLabel = QLabel('Select # of Graphs')
        self.numGraphLabel.setFixedHeight(20)
        self.comboBox = QComboBox()
        self.comboBox.setToolTip('# of Graphs')
        for i in range(5):
            self.comboBox.addItem('%s' % (2**i))
        self.comboBox.setCurrentIndex(4)
        self.comboBox.currentIndexChanged.connect(self.graphshift)

        self.numGraphsLayout.addWidget(self.numGraphLabel)
        self.numGraphsLayout.addWidget(self.comboBox)
        self.numGraphs.setLayout(self.numGraphsLayout)

        # Data selection menu
        self.data_list = QtGui.QWidget()
        self.data_list_layout = QVBoxLayout()

        sensor_list = ('RPM', 'Speed')
        for data_type in sensor_list:
            item = QCheckBox(data_type)
            self.data_list_layout.addWidget(item)
        self.data_list.setLayout(self.data_list_layout)

        # Place buttons in dock widget section
        self.dock = QDockWidget("Graph Options", self)
        self.dock_widget = QtGui.QWidget() # Set up widget to put buttons in
        self.dock_layout = QtGui.QVBoxLayout() # Layout for buttons

        self.dock_layout.addWidget(self.numGraphs)
        self.dock_layout.addWidget(self.data_list)
        self.dock_widget.setLayout(self.dock_layout) # Apply button layout to button widget
        self.dock.setWidget(self.dock_widget) # Set dock widget to contain buttons

        # Display dock widget and set its attributes
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

        self.toolTestGraph = QAction(QIcon('icons/graphic-card.png'), 'Graph', self)
        self.toolTestGraph.setStatusTip('Graphs')
        self.toolTestGraph.setCheckable(True)
        self.toolTestGraph.triggered.connect(self.displayTestGraph)

        # Add toolbar to left side
        self.toolbar = QtWidgets.QToolBar('Red')
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

        self.toolbar.addAction(self.toolHome)
        self.toolbar.addAction(self.toolTestGraph)

    def initMenuBar(self):
        # Init a menu bar
        menubar = self.menuBar()

        # Main menu options
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
        newAction = QAction('Test', self)
        editMenu.addAction(newAction)
        # --------------------------------------------------------

    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append( randint(0,100))  # Add a new random value.
        # self.z = self.z[1:]  # Remove the first
        # self.z.append(randint(0, 100))  # Add a new random value.
        # self.sin = self.sin[1:]
        # self.sin.append(np.sin(self.x[-1]) + 50)

        for row in self.GraphClass.graph_array:
            # Process events from OS to reduce input lag
            QApplication.processEvents()
            for graph in row:
                graph.plot(self.x, self.y, pen=self.pen, clear=True)

    def graphshift(self):
        self.GraphClass.showGraphs(self.comboBox.currentText())
        self.graphs_shown = int(self.comboBox.currentText())
        if self.graphs_shown == 1:
            for i in range(1,16):
                self.graph_select_buttons.button(i).setEnabled(False)


    def displayHome(self):
        self.Stack.setCurrentIndex(0)
        self.dock.hide()
        self.toolHome.setChecked(True)
        self.toolTestGraph.setChecked(False)

    def displayTestGraph(self):
        self.Stack.setCurrentIndex(1)
        self.dock.show()
        self.toolHome.setChecked(False)
        self.toolTestGraph.setChecked(True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    l = SplashScreen()
    l.show()
    w = MainWindow()


    # Progresses loading bar and shows main app once complete
    def showViewer():
        if l.counter == 100:
            w.showMaximized()
        l.progress()

    # Sets a timer to check loading progress
    timer = QtCore.QTimer()
    timer.timeout.connect(showViewer)
    timer.start(5)

    app.setAttribute(QtCore.Qt.AA_Use96Dpi) # Helps with window alignments
    sys.exit(app.exec_())
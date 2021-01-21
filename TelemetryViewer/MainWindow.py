import sys
import time
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog
from PyQt5.Qt import *

from MainWindowroot import Ui_MainWindow
from FileBrowser import Open
from FileSaver import Save
from GraphManager import GraphManager
from Loader import SplashScreen as Loader
import Serial


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Better sizing for page selection menu
        self.ui.frame_left_menu.setMinimumWidth(100)

        ## Pages-------------------------------------------------------------------------------------------------------
        ##Home Page
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        self.ui.btn_home.setCheckable(True)
        self.ui.btn_home.setChecked(True)
        self.ui.btn_home.setIcon(QIcon('icons/home.png'))

        ##Setup Page
        self.ui.btn_page_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.setup_page))
        self.ui.btn_page_2.setCheckable(True)
        self.ui.import_btn.clicked.connect(Open)
        self.ui.btn_page_2.setIcon(QIcon('icons/wrench-screwdriver.png')) # /wrench /script-attribute-s
        self.comPortComboBox = comPortComboBox(self) # Generate custom COM port menu
        self.ui.horizontalLayout_4.replaceWidget(self.ui.port_combobox, self.comPortComboBox) # Places custom COM port menu in setup layout
        self.ui.port_combobox.close() # CLoses old COM port menu
        self.ui.serial_btn.clicked.connect(lambda: self.serialbtn) # Connect functions to serial button

        ##Graph Page
        self.ui.graph_page.setStyleSheet("background-color: rgb(35, 35, 35)") # Sets background of graph page
        # Initializing GraphManager onto graph page
        self.GraphManager = GraphManager(self)
        self.ui.horizontalLayout_7.removeWidget(self.ui.configMenu) # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.GraphManager) # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.ui.configMenu) # Reorganize widgets
        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_page))
        self.ui.btn_page_3.setCheckable(True)
        self.ui.btn_page_3.setIcon( QIcon('icons/system-monitor.png'))  # /blue-document-block /system-monitor /application-wave
        # Graph page functions
        self.ui.graphtype_comboBox.currentIndexChanged.connect(self.menuchange)
        self.ui.importlayout_btn.clicked.connect(Open)
        self.ui.savelayout_btn.clicked.connect(Save)
        self.ui.hideConfig_btn.clicked.connect(self.ui.configMenu.hide) # Hides configuration menu when clicked
        self.ui.configMenu.hide() # Initially hide configuration menu
        self.ui.graphnum_comboBox.currentIndexChanged.connect(lambda: self.GraphManager.showGraphs(self.ui.graphnum_comboBox.currentText())) # Change number of graphs shown when combobox value changed
        self.ui.graphnum_comboBox.setCurrentIndex(self.ui.graphnum_comboBox.count()-1) # Initialize number of shown graphs to maximum

        ##Command Page
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))
        self.ui.btn_page_4.setCheckable(True)
        self.ui.btn_page_4.setIcon(QIcon('icons/application-terminal.png'))

        # Add page buttons to a group for better control
        self.page_btn_group = QButtonGroup()
        self.page_btn_group.setExclusive(True)
        self.page_btn_group.addButton(self.ui.btn_home)
        self.page_btn_group.addButton(self.ui.btn_page_2)
        self.page_btn_group.addButton(self.ui.btn_page_3)
        self.page_btn_group.addButton(self.ui.btn_page_4)
        # Set style sheet of all buttons
        for button in self.page_btn_group.buttons():
            button.setStyleSheet("QPushButton {\n"
                "    color: rgb(255, 255, 255);\n"
                "    background-color: rgb(35, 35, 35);\n"
                "    border: 0px solid;\n"
                "}\n"
                "QPushButton:hover {\n"
                "    background-color: rgb(85, 85, 85);\n"
                "}"
                "QPushButton:checked {\n"
                "    background-color: rgb(100, 100, 100);\n"
                "}")
        ## End of Pages-------------------------------------------------------------------------------------------------------

        #####color = QColorDialog.getColor()##### sets up color opening window

        # Timer for testing graphing -> calls update function
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.GraphManager.update)
        self.timer.start()
        print(self.availableCOMPorts())


    def menuchange(self, i):
        configtext = (self.ui.graphtype_comboBox.currentText())
        if configtext == "Time Domain":
            self.ui.configMenuStack.setCurrentWidget(self.ui.timeDomain_page)
        elif configtext == "Polar Plot":
            self.ui.configMenuStack.setCurrentWidget(self.ui.polarPlot_page)
        elif configtext == "RPM Gauge":
            self.ui.configMenuStack.setCurrentWidget(self.ui.rpm_page)
        elif configtext == "Speedo Gauge":
            self.ui.configMenuStack.setCurrentWidget(self.ui.speedo_page)

    #TODO This code allows us to see available COM ports and return using the portlist array. (NOT CALLED ATM)
    #TODO Now just need to know when to call this function (start of running or call, or always?) and also be able to
    #TODO    return the list of ports, also we can send more data back (ask me - Roy)
    def availableCOMPorts(self):        # Generates a list of available COM ports
        portlist = serial.tools.list_ports.comports(include_links=False)
        portlistarray = []
        for element in portlist:
            portlistarray.append(element.device)
        return portlistarray # Should return a list of strings if possible -> ['COM1', 'COM4']

    def serialbtn(self):
        if self.ui.serial_btn.text()=="Connect":
            port=self.ui.port_combobox.currentText()
            print (port)
            self.ui.serial_btn.setText("Disconnect")
        else:
            self.ui.serial_btn.setText("Connect")

    def editMenuCalled(self, plotWidget):
        self.currentPlotWidget = plotWidget
        self.currentPlotWidget.setBackground('g')
        self.currentPlotWidget.getPlotItem().setLabel('bottom', text='test')
        self.ui.configMenu.show()
        print('GUI connected')

    def configApply(self):
        return

class comPortComboBox(QtWidgets.QComboBox):
    populateCOMSelect = QtCore.pyqtSignal()

    def __init__(self, parentWidget):
        super(comPortComboBox, self).__init__()
        self.parentWidget = parentWidget
        self.setStyleSheet('background-color: rgb(255,255,255);' 'selection-background-color: rgb(168,168,168);')
        self.setMaximumWidth(100)
        self.addItem('test')
        self.populateCOMSelect.connect(self.populateComboBox)

    def showPopup(self):
        self.populateCOMSelect.emit()
        super(comPortComboBox, self).showPopup()

    def populateComboBox(self):
        self.clear()
        for port in self.parentWidget.availableCOMPorts():
            self.addItem(port)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)  # Helps with window alignments
    window = MainWindow()
    loader = Loader()
    loader.show()

    def loaderProgress():
        #TODO Turn loader back on
        # loader.counter = 100

        if loader.counter == 100:
            timer.stop()
            window.show()
            loader.close()
        loader.progress()

    # Sets a timer to check loading progress
    timer = QtCore.QTimer()
    timer.timeout.connect(loaderProgress)
    timer.start(5)

    app.setAttribute(QtCore.Qt.AA_Use96Dpi)  # Helps with window alignments
    sys.exit(app.exec_())

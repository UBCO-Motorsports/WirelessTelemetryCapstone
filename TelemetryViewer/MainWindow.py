import sys
import time
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog
from PyQt5.Qt import *
import json

from MainWindowroot import Ui_MainWindow
from FileBrowser import Open
from FileSaver import Save
from GraphManager import GraphManager
from Loader import SplashScreen as Loader
import Serial
Canfilename=""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Serial not initially connected at start up
        self.serialConnected = False

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
        self.ui.btn_page_2.setIcon(QIcon('icons/wrench-screwdriver.png'))  # /wrench /script-attribute-s
        self.comPortComboBox = comPortComboBox(self)  # Generate custom COM port menu
        self.ui.horizontalLayout_4.replaceWidget(self.ui.port_combobox,
                                                 self.comPortComboBox)  # Places custom COM port menu in setup layout
        self.ui.port_combobox.close()  # CLoses old COM port menu
        self.ui.serial_btn.clicked.connect(self.connectSerial)  # Connect functions to serial button
        self.ui.import_btn.clicked.connect(self.canJson)
        self.ui.tableWidget.cellClicked.connect(self.tabletolist)
        self.ui.listWidget.itemClicked.connect(self.listremove)
        self.ui.apply_btn.clicked.connect(self.applytoConfig)

        ##Graph Page
        self.ui.graph_page.setStyleSheet("background-color: rgb(35, 35, 35)")  # Sets background of graph page
        # Initializing GraphManager onto graph page
        self.GraphManager = GraphManager(self)
        self.ui.horizontalLayout_7.removeWidget(self.ui.configMenu) # Reorganize widgets
        self.ui.horizontalLayout_7.removeWidget(self.ui.graph_widget) # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.GraphManager) # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.ui.configMenu) # Reorganize widgets
        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_page))
        self.ui.btn_page_3.setCheckable(True)
        self.ui.btn_page_3.setIcon(
            QIcon('icons/system-monitor.png'))  # /blue-document-block /system-monitor /application-wave
        # Graph page functions
        self.ui.graphtype_comboBox.currentIndexChanged.connect(self.menuchange)
        self.ui.importlayout_btn.clicked.connect(Open)
        self.ui.savelayout_btn.clicked.connect(Save)
        self.ui.hideConfig_btn.clicked.connect(self.ui.configMenu.hide) # Hides configuration menu when clicked
        self.ui.configMenu.hide() # Initially hide configuration menu
        self.ui.graphnum_comboBox.currentIndexChanged.connect(lambda: self.GraphManager.showGraphs(self.ui.graphnum_comboBox.currentText())) # Change number of graphs shown when combobox value changed
        self.ui.graphnum_comboBox.setCurrentIndex(self.ui.graphnum_comboBox.count()-1) # Initialize number of shown graphs to maximum
        self.ui.applyconfig_btn.clicked.connect(self.configApply)


        ##Command Page
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))
        self.ui.btn_page_4.setCheckable(True)
        self.ui.btn_page_4.setIcon(QIcon('icons/application-terminal.png'))
        self.ui.EmergencyShutdown_btn.clicked.connect(lambda: self.GraphManager.SerialModule.sendCommand("s\r"))
        self.ui.pushButton_2.clicked.connect(lambda: self.GraphManager.SerialModule.sendCommand("r\r"))
        self.ui.pushButton.clicked.connect(lambda: self.sendcommandfromBox())
        self.ui.commandbox.returnPressed.connect(lambda: self.sendcommandfromBox())
        self.ui.listWidget_2.clicked.connect(lambda: self.sendcommandfromList())

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

        # Timer for testing graphing -> calls update function
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.GraphManager.update)
        self.timer.start()
        print(self.availableCOMPorts())

    def applytoConfig(self):
        with open('itemslogged.json', 'r+') as json_file:
            data = json.load(json_file)
            json_file.close()
        layout = QVBoxLayout()
        self.radiodict={}
        for i in range(len(data["logged"])):
            name = data["logged"][i]['Name']
            id = data["logged"][i]['ID']
            units = data["logged"][i]['Units']
            scale = data["logged"][i]['Scale']
            position = data["logged"][i]['Position']
            size = data["logged"][i]['Size']
            offset = data["logged"][i]['Offset']
            color = data["logged"][i]['Color']
            self.radiodict[i]=QCheckBox(name)
            self.ui.comboBox_3.addItem(name)
            self.ui.comboBox_4.addItem(name)
            self.ui.comboBox_5.addItem(name)
            self.ui.comboBox.addItem(name)
        for i in self.radiodict.items():
            layout.addWidget(i[1])
        self.ui.scrollArea.setLayout(layout)



            #TODO make it so radio buttons refresh after hitting apply on setup again


    def sendcommandfromList(self):
        self.GraphManager.SerialModule.sendCommand(self.ui.listWidget_2.currentItem().text())

    def sendcommandfromBox(self):
        text=self.ui.commandbox.text()
        self.ui.commandbox.clear()
        self.GraphManager.SerialModule.sendCommand(text)

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

    # TODO This code allows us to see available COM ports and return using the portlist array. (NOT CALLED ATM)
    # TODO Now just need to know when to call this function (start of running or call, or always?) and also be able to
    # TODO    return the list of ports, also we can send more data back (ask me - Roy)
    def availableCOMPorts(self):  # Generates a list of available COM ports testing
        portlist = serial.tools.list_ports.comports(include_links=False)
        portlistarray = []
        for element in portlist:
            portlistarray.append(element.device)
        return portlistarray  # Should return a list of strings if possible -> ['COM1', 'COM4']

    def connectSerial(self):
        if self.ui.serial_btn.text() == 'Connect':
            if self.GraphManager.SerialModule.tryConnectSerial(self.comPortComboBox.currentText()):
                self.ui.serial_btn.setText("Disconnect")
                self.serialConnected = True
            else:
                self.ui.serial_btn.setText("Connect")
                self.serialConnected = False
        else:
            self.GraphManager.SerialModule.tryConnectSerial(self.ui.serial_btn.text())
            self.ui.serial_btn.setText('Connect')
            self.serialConnected = False

    def editMenuCalled(self, plotWidget):
        self.currentPlotWidget = plotWidget
        self.currentPlotWidget.setBackground('g')
        self.currentPlotWidget.getPlotItem().setLabel('bottom', text='test')
        self.ui.configMenu.show()

    def configApply(self):
        self.currentPlotWidget.setBackground('b')
        self.currentPlotWidget.yData = self.GraphManager.z
        return

    def canJson(self):
        global Canfilename
        p = 0
        filelookup = Open()
        file = filelookup.openFileNameDialog()
        Canfilename=file
        if file != "":
            while (self.ui.tableWidget.rowCount() > 0):
                self.ui.tableWidget.removeRow(0)

            with open(file) as json_file:
                data = json.load(json_file)
                for i in data["Haltech"]:
                    self.ui.tableWidget.insertRow(p)
                    self.ui.tableWidget.setItem(p, 0, QtGui.QTableWidgetItem("Click to Select"))
                    self.ui.tableWidget.setItem(p, 1, QtGui.QTableWidgetItem(i['Name']))
                    self.ui.tableWidget.setItem(p, 2, QtGui.QTableWidgetItem(str(i['Scale'])))
                    self.ui.tableWidget.setItem(p, 3, QtGui.QTableWidgetItem(i['ID']))
                    p = p + 1
                json_file.close()
            self.ui.listWidget.clear()
            with open('itemslogged.json', 'w+') as jsonlist:
                data = {}
                data['logged'] = []
                json.dump(data, jsonlist, indent=4)
                jsonlist.close()

    def tabletolist(self, row, column):
        global Canfilename
        found = False
        for i in range(self.ui.listWidget.count()):
            if self.ui.listWidget.item(i).text() == self.ui.tableWidget.item(row, 1).text():
                found = True
        if not found:
            color = QColorDialog.getColor()
            color2 = color.getRgb()
            if color.isValid():
                with open(Canfilename, 'r+') as json_file:
                    data= json.load(json_file)
                    datafromcan=data["Haltech"][int(row)]
                    json_file.close()

                self.jsonlogged(datafromcan, str(color2), self.ui.listWidget.count())

                self.ui.listWidget.addItem(self.ui.tableWidget.item(row, 1).text())
                for j in range(self.ui.tableWidget.columnCount()):
                    self.ui.tableWidget.item(row, j).setBackground(QColor.fromRgb(150, 150, 150))
                if self.ui.listWidget.item(0).text() == "None Selected":
                    self.ui.listWidget.takeItem(0)

    def jsonlogged(self, datafromcan, color, i):
        with open('itemslogged.json', 'r+') as json_file:
            data = json.load(json_file)
            data["logged"].append(datafromcan)
            data["logged"][i]['Color']=color
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.close()

    def listremove(self, row):
        i = self.ui.listWidget.currentRow()
        listtext = self.ui.listWidget.currentItem().text()
        if listtext != "None Selected":
            for j in range(self.ui.tableWidget.rowCount()):
                if listtext == self.ui.tableWidget.item(j, 1).text():
                    for k in range(self.ui.tableWidget.columnCount()):
                        self.ui.tableWidget.item(j, k).setBackground(QColor.fromRgb(190, 190, 190))
            with open('itemslogged.json', 'r+') as json_file:
                data = json.load(json_file)
                del data["logged"][i]
                json_file.seek(0)
                json_file.close()
            with open('itemslogged.json', 'w+') as json_file:
                json.dump(data, json_file, indent=4)
                json_file.close()

            self.ui.listWidget.takeItem(i)

        if self.ui.listWidget.count() == 0:
            self.ui.listWidget.addItem("None Selected")


class comPortComboBox(QtWidgets.QComboBox):
    populateCOMSelect = QtCore.pyqtSignal()

    def __init__(self, parentWidget):
        super(comPortComboBox, self).__init__()
        self.parentWidget = parentWidget
        self.setStyleSheet('background-color: rgb(255,255,255);' 'selection-background-color: rgb(168,168,168);')
        self.setMinimumWidth(80)
        self.setMaximumWidth(160)
        self.addItem('Select COM port')
        self.populateCOMSelect.connect(self.populateComboBox)

    def showPopup(self):
        self.populateCOMSelect.emit()
        super(comPortComboBox, self).showPopup()

    # Calls for a list of available COM ports and populates them to the combobox
    def populateComboBox(self):
        self.clear()
        ports = self.parentWidget.availableCOMPorts()
        if not ports:  # Check if list of ports is empty
            self.parentWidget.ui.serial_btn.setDisabled(True)
            self.addItem('No active COM ports')
        else:
            self.parentWidget.ui.serial_btn.setDisabled(False)
            for port in ports:
                self.addItem(port)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)  # Helps with window alignments
    window = MainWindow()
    loader = Loader()
    loader.show()


    def loaderProgress():
        # TODO Turn loader back on
        loader.counter = 100

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

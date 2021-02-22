import sys
import random
import time
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog
from PyQt5.Qt import *
import json
from PyQt5.QtCore import QObject,QThread,pyqtSignal
import re # Useful for stripping characters from strings
from MainWindowroot import Ui_MainWindow
from FileBrowser import Open
from FileSaver import Save
from GraphManager import GraphManager
from Loader import SplashScreen as Loader
# from threading import *
import Serial
# Canfilename=""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.defaultFile = 'CANBUS/CANBUS2.json'
        self.Canfilename = 'CANBUS/CANBUS2.json'
        self.selected_channels = []
        self.configData = []

        # Better sizing for page selection menu
        self.ui.frame_left_menu.setMinimumWidth(100)
        # self.ui.frame_pages.setStyleSheet('background-color: rgb(85,85,85);')

        # Initialize page selection buttons
        self.initPageButtons()

        # Initialize Setup Page
        self.initSetupPage()
        # Initialize Graph Page
        self.initGraphPage()
        # Initialize configuration menu
        self.initConfigMenu()
        # Initialize Command Page
        self.initCommandPage()

        # Serial not initially connected at start up
        self.serialConnected = False
        self.messagebuffer = []
        self.GraphManager.SerialModule.ResetMethod = self.applytoConfig

        self.sendThread = SendThread(self.sendMessages)

        # Timer for testing graphing -> calls update function
        self.timer = QtCore.QTimer()
        # DO NOT CHANGE! WORKS SOMEHOW
        self.timer.setInterval(75)
        self.timer.timeout.connect(self.GraphManager.update)
        self.timer.start()

        # self.threadpool = QThreadPool()
        # print('Multithreading with max of %d threads' % self.threadpool.maxThreadCount())
        # self.sendWorker = Worker(self.sendMessages, MainWindow=self, GraphManager=self.GraphManager)
        # self.timer.timeout.connect(lambda: print(f'Current threads: {self.threadpool.activeThreadCount()}\n'))

    def initPageButtons(self):
        # Add page selection buttons to a group for better control
        self.page_btn_group = QButtonGroup()
        self.page_btn_group.setExclusive(True)  # Only one button selected at a time
        self.page_btn_group.addButton(self.ui.btn_home)
        self.page_btn_group.addButton(self.ui.btn_page_2)
        self.page_btn_group.addButton(self.ui.btn_page_3)
        self.page_btn_group.addButton(self.ui.btn_page_4)
        for button in self.page_btn_group.buttons():
            # Make all buttons checkable
            button.setCheckable(True)
            # Set style sheet of all buttons
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

        # Set home page as initial widget
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.ui.btn_home.setChecked(True)

        # Connect page buttons
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        self.ui.btn_page_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.setup_page))
        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_page))
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))

        # Set icons for each page button
        self.ui.btn_home.setIcon(QIcon('icons/home.png'))
        self.ui.btn_page_2.setIcon(QIcon('icons/wrench-screwdriver.png'))  # /wrench /script-attribute-s
        self.ui.btn_page_3.setIcon(QIcon('icons/system-monitor.png'))  #  /system-monitor /application-wave
        self.ui.btn_page_4.setIcon(QIcon('icons/application-terminal.png'))

    def initSetupPage(self):
        # Custom COM port menu (combo box)
        self.comPortComboBox = comPortComboBox(self)  # Generate custom COM port menu
        self.ui.horizontalLayout_4.replaceWidget(self.ui.port_combobox, self.comPortComboBox)  # Places custom COM port menu in setup layout
        self.ui.port_combobox.close()  # CLoses old COM port menu

        self.ui.serial_btn.clicked.connect(self.connectSerial)  # Connect functions to serial button
        self.ui.refresh_btn.clicked.connect(self.comPortComboBox.populateCOMSelect)  # Populate COM port menu when clicked
        self.ui.import_btn.clicked.connect(self.canJson)
        self.ui.tableWidget.cellClicked.connect(self.tabletolist)
        self.ui.listWidget.itemClicked.connect(self.listremove)

        self.ui.apply_btn.setEnabled(True)
        self.ui.savetodefault.clicked.connect(self.savetodefaultlist)
        self.ui.pushButton_3.clicked.connect(self.connectdefaulttolist)

        # Button shortcuts
        self.ui.import_btn.setShortcut('i')
        self.ui.default_btn.clicked.connect(self.defaultJson)
        self.ui.default_btn.setShortcut('d')
        self.ui.pushButton_3.clicked.connect(self.connectdefaulttolist)
        self.ui.pushButton_3.setShortcut('Shift+d')
        self.ui.apply_btn.clicked.connect(self.applytoConfig)
        self.ui.apply_btn.setShortcut('Shift+a')

    def initGraphPage(self):
        # Initializing GraphManager onto graph page
        self.GraphManager = GraphManager(self)
        self.ui.horizontalLayout_7.removeWidget(self.ui.configMenu)  # Reorganize widgets
        self.ui.horizontalLayout_7.removeWidget(self.ui.graph_widget)  # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.GraphManager)  # Reorganize widgets
        self.ui.horizontalLayout_7.addWidget(self.ui.configMenu)  # Reorganize widgets

        # Graph page functions
        self.ui.graphtype_comboBox.currentIndexChanged.connect(self.menuchange)
        # TODO 'Log Default' functionality
        self.ui.importlayout_btn.clicked.connect(self.importlayout)  # TODO
        self.ui.savelayout_btn.clicked.connect(self.savelayout)  # TODO

        self.ui.graphnum_comboBox.currentIndexChanged.connect(lambda: self.GraphManager.showGraphs(self.ui.graphnum_comboBox.currentText()))  # Change number of graphs shown when combobox value changed
        self.ui.graphnum_comboBox.setCurrentIndex(self.ui.graphnum_comboBox.count() - 1)  # Initialize number of shown graphs to maximum

    def initConfigMenu(self):
        # Initialize scroll widget for available data channels
        self.data_layout = QVBoxLayout()
        self.scrollWidget = QWidget()
        self.ui.scrollArea.setWidget(self.scrollWidget)
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Time domain y-ranging
        self.ui.checkBox.setChecked(True)
        self.ui.lineEdit_5.setDisabled(True)
        self.ui.lineEdit_6.setDisabled(True)
        self.ui.checkBox.stateChanged.connect(lambda: self.autorangeEnable(self.ui.checkBox, self.ui.lineEdit_5, self.ui.lineEdit_6))

        # Polar plot ranging
        self.ui.checkBox_2.stateChanged.connect(lambda: self.autorangeEnable(self.ui.checkBox_2, self.ui.lineEdit_10, self.ui.lineEdit_11))
        self.ui.checkBox_3.stateChanged.connect(lambda: self.autorangeEnable(self.ui.checkBox_3, self.ui.lineEdit_12, self.ui.lineEdit_13))

        # Hide button
        # self.ui.hideConfig_btn.clicked.connect(self.ui.configMenu.hide)  # Hides configuration menu when clicked
        self.ui.hideConfig_btn.setShortcut('h')
        self.ui.hideConfig_btn.clicked.connect(self.configHide)

        self.ui.configMenu.hide()  # Initially hide configuration menu

        # Apply button
        self.ui.applyconfig_btn.clicked.connect(self.configApply)

    def importlayout(self):
        filelookup = Open()
        file = filelookup.openFileNameDialog()
        layoutfile = file
        if layoutfile != "":
            with open(layoutfile, 'r+') as json_1:
                layout = json.load(json_1)
                json_1.close()
        print(layout)
        self.GraphManager.importLayout(layout['layout'])


    def savelayout(self):
        graph_layout_dict = {'layout': []}

        for row in self.GraphManager.graph_array:
            row_layout = []
            for graph in row:
                graph_dict = {}

                # Saves basic widget data
                graph_dict['type'] = graph.type
                graph_dict['datasets'] = graph.yData

                # Saves widget specific data
                if graph.type == 'Time Domain':
                    graph_dict['title'] = graph.title
                    graph_dict['xLabel'] = graph.xLabel
                    graph_dict['yLabel'] = graph.yLabel
                    graph_dict['yRange'] = graph.yRange
                    graph_dict['autoRange'] = graph.autoRange
                elif graph.type == 'Polar Plot':
                    graph_dict['title'] = graph.title
                    graph_dict['xData'] = graph.xData
                    graph_dict['xLabel'] = graph.xLabel
                    graph_dict['yLabel'] = graph.yLabel
                    graph_dict['yRange'] = graph.yRange
                    graph_dict['yAutoRange'] = graph.yAutoRange
                    graph_dict['xRange'] = graph.xRange
                    graph_dict['xAutoRange'] = graph.xAutoRange
                    graph_dict['samples'] = graph.samples

                row_layout.append(graph_dict)
            graph_layout_dict['layout'].append(row_layout)

        print(graph_layout_dict)

        filelookup = Save()
        file = filelookup.saveFileDialog()
        layoutfile = file
        # layoutfile = 'graphlayout.json'
        if layoutfile != "":
            with open(layoutfile, 'w+') as json_1:
                json.dump(graph_layout_dict, json_1, indent=4)
                json_1.close()

    def initCommandPage(self):
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))
        self.ui.btn_page_4.setCheckable(True)
        self.ui.btn_page_4.setIcon(QIcon('icons/application-terminal.png'))
        self.ui.EmergencyShutdown_btn.clicked.connect(lambda: self.GraphManager.SerialModule.sendCommand("s\r"))
        self.ui.pushButton_2.clicked.connect(lambda: self.GraphManager.SerialModule.sendCommand("r\r"))
        self.ui.pushButton.clicked.connect(lambda: self.sendcommandfromBox())
        self.ui.commandbox.returnPressed.connect(lambda: self.sendcommandfromBox())
        self.ui.listWidget_2.clicked.connect(lambda: self.sendcommandfromList())

    def autorangeEnable(self, checkBox, lineEdit, lineEdit2):
        if checkBox.isChecked():
            lineEdit.setDisabled(True)
            lineEdit2.setDisabled(True)
        else:
            lineEdit.setDisabled(False)
            lineEdit2.setDisabled(False)

    def connectdefaulttolist(self):
        # Checks if table is empty
        if self.ui.tableWidget.item(0, 1) is None:
            self.defaultJson()

        with open('defaultitems.json', 'r+') as json_1:
            data = json.load(json_1)
            json_1.close()
        with open('itemslogged.json', 'w+') as json_2:
            json.dump(data, json_2, indent=4)
            json_2.close()
        self.ui.listWidget.clear()
        for i in range(len(data["logged"])):
            self.ui.listWidget.addItem(data["logged"][i]["Name"])
            item = self.ui.listWidget.item(i)
            colorRGB = self.getColor(data["logged"][i]['Color'])
            # color = data["logged"][i]['Color']
            # color = re.sub(r'[()]', '', color)  # Gets rid of brackets from color value
            # colorRGB = [int(c) for c in color.split(',')]  # Orders the RGBA values obtained from JSON
            iconPixmap = QPixmap(32, 32)
            iconPixmap.fill(QColor.fromRgb(colorRGB[0],colorRGB[1],colorRGB[2]))
            item.setIcon(QIcon(iconPixmap))
        self.ui.label_36.setText(str(self.ui.listWidget.count()) + '/16 Channels Selected')
        self.ui.label_37.setText('Not Applied')
        self.ui.label_37.setStyleSheet('color: rgb(255, 0, 0);')

    def getColor(self, rgba):
        colorRGBA = re.sub(r'[()]', '', rgba)
        colorRGB = [int(c) for c in colorRGBA.split(',')]
        return colorRGB

    def savetodefaultlist(self):
        with open('itemslogged.json', 'r+') as json_1:
            data = json.load(json_1)
            json_1.close()
        with open('defaultitems.json', 'w+') as json_2:
            json.dump(data, json_2, indent=4)
            json_2.close()

    def applytoConfig(self):

        with open('itemslogged.json', 'r+') as json_file:
            data = json.load(json_file)
            json_file.close()

        # self.datadict = data
        # # self.datadict["logged"][0]["buffer"]=["heloo","test"]
        #TODO update selected_channels while keeping buffers coherent
        self.selected_channels.clear()
        self.selected_channels = data
        print(self.selected_channels)

        self.GraphManager.SerialModule.recievedataDict(self.selected_channels)  # Sending dataDict (list of data types being recieved) to Serial to scale -Roy
        # print(self.datadict["logged"][0])
        # print(self.datadict["logged"][0]["ID"])

        self.ui.comboBox_5.clear()
        self.ui.comboBox.clear()
        self.ui.comboBox_4.clear()
        self.ui.comboBox_3.clear()

        for i in reversed(range(self.data_layout.count())):
            self.data_layout.itemAt(i).widget().setParent(None)
        self.configData.clear()
        self.messagebuffer.clear()
        for i in range(len(data["logged"])):
            name = data["logged"][i]['Name']
            id = data["logged"][i]['ID']
            units = data["logged"][i]['Units']
            scale = data["logged"][i]['Scale']
            position = data["logged"][i]['Position']
            size = data["logged"][i]['Size']
            offset = data["logged"][i]['Offset']
            color = data["logged"][i]['Color']

            # Constructs the check box items in the config menu and sets the colored icon
            self.configData.append(QCheckBox(name))
            configPixmap = QPixmap(32, 32)
            colorRGB = self.getColor(color)
            configPixmap.fill(QColor.fromRgb(colorRGB[0], colorRGB[1], colorRGB[2]))
            self.configData[i].setIcon(QIcon(configPixmap))
            self.configData[i].setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            self.ui.comboBox_3.addItem(name)
            self.ui.comboBox_4.addItem(name)
            self.ui.comboBox_5.addItem(name)
            self.ui.comboBox.addItem(name)

            # List of channels to send to controller
            # f0 0864 00 16
            #f0 000 00 00
            message = "f" + str(i).zfill(2) + " " + str(int(id,16)).zfill(4) + " " + str(position).zfill(2) + " " + str(size).zfill(2) + "\r"
            self.messagebuffer.append(message)

        if len(self.messagebuffer)<16:
            messagefill =16-len(self.messagebuffer)
            length=len(self.messagebuffer)
        else:
            messagefill=0

        for i in range(messagefill):
            self.messagebuffer.append("f"+str(i+length).zfill(2) + " 0000 00 16\r")

        # Add checkboxes to config menu scroll area
        for i in self.configData:
            self.data_layout.addWidget(i)
        self.scrollWidget.setLayout(self.data_layout)

        # self.ui.apply_btn.setDisabled(True)
        # self.ui.apply_btn.setText('Sending...')
        # self.sendMessages()
        # self.ui.apply_btn.setDisabled(False)
        # self.ui.apply_btn.setText('Apply')

        self.sendThread.start()

    def sendMessages(self):
        #self.GraphManager.SerialModule.sendCommand("r\r")
        self.ui.apply_btn.setText('Sending...')
        self.ui.apply_btn.setDisabled(True)
        for messages in self.messagebuffer:
            if self.GraphManager.SerialModule.serialConnected:
                self.GraphManager.SerialModule.sendCommand(messages)
                time.sleep(0.3)
            print(messages)
        self.ui.apply_btn.setText('Apply')
        self.ui.apply_btn.setDisabled(False)
        self.ui.label_37.setText('Applied')
        self.ui.label_37.setStyleSheet('color: rgb(0, 255, 0);')

    def sendcommandfromList(self):
        self.GraphManager.SerialModule.sendCommand(self.ui.listWidget_2.currentItem().text()+"\r")

    def sendcommandfromBox(self):
        text=self.ui.commandbox.text()
        self.ui.commandbox.clear()
        self.GraphManager.SerialModule.sendCommand(text+"\r")

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

    # This code allows us to see available COM ports and return using the portlist array.
    def availableCOMPorts(self):  # Generates a list of available COM ports testing
        portlist = serial.tools.list_ports.comports(include_links=False)
        portlistarray = []
        for port in portlist:
            portlistarray.append(port.device)
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

    def configMenuCalled(self, plotWidget):
        # Clears selection border on previous graph
        try:
            self.currentPlotWidget.getPlotItem().getViewBox().setBorder(None)
        except:
            pass
        try:
            self.currentPlotWidget.ui.frame_3.setStyleSheet('background-color: rgb(216, 216, 216);')
            self.currentPlotWidget.highlighted = False
        except:
            pass

        # Sets the passed in widget to be the currently selected widget
        self.currentPlotWidget = plotWidget

        # TODO reset configuration menu to the current plotwidget data\
        if plotWidget.type == 'Time Domain':
            self.currentPlotItem = self.currentPlotWidget.getPlotItem()
            self.currentPlotItem.getViewBox().setBorder(color=(0,255,0),width=3)
            if self.configData:
                for checkbox in self.configData:
                    checkbox.setChecked(False)
                for i in self.currentPlotWidget.yData:
                    self.configData[i].setChecked(True)

            if self.currentPlotWidget.autoRange:
                self.ui.checkBox.setChecked(True)
                self.ui.lineEdit_5.setDisabled(True)
                self.ui.lineEdit_6.setDisabled(True)
            else:
                self.ui.checkBox.setChecked(False)
                self.ui.lineEdit_5.setDisabled(False)
                self.ui.lineEdit_6.setDisabled(False)
                self.ui.lineEdit_5.setText(str(self.currentPlotWidget.yRange[0]))
                self.ui.lineEdit_6.setText(str(self.currentPlotWidget.yRange[1]))
            self.ui.lineEdit_2.setText(self.currentPlotWidget.title)
            self.ui.lineEdit_3.setText(self.currentPlotWidget.yLabel)
            self.ui.lineEdit_4.setText(self.currentPlotWidget.xLabel)

            self.ui.configMenuStack.setCurrentWidget(self.ui.timeDomain_page)
            self.ui.graphtype_comboBox.setCurrentIndex(0)

        elif plotWidget.type == 'Polar Plot':
            self.currentPlotItem = self.currentPlotWidget.getPlotItem()
            self.currentPlotItem.getViewBox().setBorder(color=(0, 255, 0), width=3)
            for checkbox in self.configData:
                checkbox.setChecked(False)
            self.ui.comboBox_3.setCurrentIndex(self.currentPlotWidget.yData[0])
            self.ui.comboBox_4.setCurrentIndex(self.currentPlotWidget.xData[0])
            self.ui.spinBox.setValue(self.currentPlotWidget.samples)

            if self.currentPlotWidget.yAutoRange:
                self.ui.checkBox_3.setChecked(True)
                self.ui.lineEdit_12.setDisabled(True)
                self.ui.lineEdit_13.setDisabled(True)
            else:
                self.ui.checkBox_3.setChecked(False)
                self.ui.lineEdit_12.setDisabled(False)
                self.ui.lineEdit_13.setDisabled(False)
                self.ui.lineEdit_12.setText(str(self.currentPlotWidget.yRange[0]))
                self.ui.lineEdit_13.setText(str(self.currentPlotWidget.yRange[1]))

            if self.currentPlotWidget.xAutoRange:
                self.ui.checkBox_2.setChecked(True)
                self.ui.lineEdit_10.setDisabled(True)
                self.ui.lineEdit_11.setDisabled(True)
            else:
                self.ui.checkBox_2.setChecked(False)
                self.ui.lineEdit_10.setDisabled(False)
                self.ui.lineEdit_11.setDisabled(False)
                self.ui.lineEdit_10.setText(str(self.currentPlotWidget.xRange[0]))
                self.ui.lineEdit_11.setText(str(self.currentPlotWidget.xRange[1]))

            self.ui.configMenuStack.setCurrentWidget(self.ui.polarPlot_page)
            self.ui.graphtype_comboBox.setCurrentIndex(1)

        elif plotWidget.type == 'RPM Gauge':
            self.ui.configMenuStack.setCurrentWidget(self.ui.rpm_page)
            self.currentPlotWidget.highlighted = True
            self.currentPlotWidget.ui.frame_3.setStyleSheet('border-radius: 150px;' 'border: 3px solid #00ff00;')
            self.ui.graphtype_comboBox.setCurrentIndex(2)
            self.ui.comboBox.setCurrentIndex(self.currentPlotWidget.yData[0])

        elif plotWidget.type == 'Speedo Gauge':
            self.ui.configMenuStack.setCurrentWidget(self.ui.speedo_page)
            self.currentPlotWidget.highlighted = True
            self.currentPlotWidget.ui.frame_3.setStyleSheet('border-radius: 150px;' 'border: 3px solid #00ff00;')
            self.ui.graphtype_comboBox.setCurrentIndex(3)
            self.ui.comboBox_5.setCurrentIndex(self.currentPlotWidget.yData[0])

        self.ui.configMenu.show()

    def configHide(self):
        self.ui.configMenu.hide()
        if self.currentPlotWidget.type == 'Time Domain' or self.currentPlotWidget.type == 'Polar Plot':
            self.currentPlotWidget.getPlotItem().getViewBox().setBorder(None)
        elif self.currentPlotWidget.type == 'RPM Gauge' or self.currentPlotWidget.type == 'Speedo Gauge':
            self.currentPlotWidget.ui.frame_3.setStyleSheet('background-color: rgb(216, 216, 216);')
            self.currentPlotWidget.highlighted = False
        else:
            pass


        # self.ui.hideConfig_btn.clicked.connect(lambda: self.currentPlotWidget.getPlotItem().getViewBox().setBorder(
        #     None))  # Clears border from currently selected plot
        # self.ui.hideConfig_btn.clicked.connect(
        #     lambda: self.currentPlotWidget.ui.frame_3.setStyleSheet('background-color: rgb(216, 216, 216);'))

    def configApply(self):
        self.currentPlotWidget = self.GraphManager.updateWidget(self.currentPlotWidget, self.ui.graphtype_comboBox.currentText())
        try:
            self.currentPlotWidget.getPlotItem().getViewBox().setBorder(color=(0,255,0),width=3)
        except:
            pass
        try:
            self.currentPlotWidget.ui.frame_3.setStyleSheet('border: 3px solid #00ff00;')
        except:
            pass

        # Autorange functionality
        if self.currentPlotWidget.type == 'Time Domain':
            if self.ui.checkBox.isChecked():
                self.ui.lineEdit_5.setDisabled(True)
                self.ui.lineEdit_6.setDisabled(True)
                self.currentPlotWidget.enableAutoRange(x=True,y=True)
                self.currentPlotWidget.autoRange = True
            else:
                # Sets y-bounds if a valid value is entered
                try:
                    self.ui.lineEdit_5.setDisabled(False)
                    self.ui.lineEdit_6.setDisabled(False)
                    self.currentPlotWidget.enableAutoRange(x=True, y=False)
                    self.currentPlotWidget.yRange = [float(self.ui.lineEdit_5.text()), float(self.ui.lineEdit_6.text())]
                    self.currentPlotWidget.setYRange(self.currentPlotWidget.yRange[0], self.currentPlotWidget.yRange[1])
                    self.currentPlotWidget.autoRange = False
                except:
                    self.ui.lineEdit_5.setDisabled(True)
                    self.ui.lineEdit_6.setDisabled(True)
                    self.ui.lineEdit_5.clear()
                    self.ui.lineEdit_6.clear()
                    self.currentPlotWidget.enableAutoRange(x=True,y=False)
                    self.ui.checkBox.setChecked(True)
                    self.currentPlotWidget.autoRange = False

            # Checks current data types to graph
            self.currentPlotWidget.yData.clear()
            for i, data_type in enumerate(self.configData):
                if data_type.isChecked():
                    self.currentPlotWidget.yData.append(i)

            # Set axes labels and title
            self.currentPlotItem = self.currentPlotWidget.getPlotItem()
            try:
                self.currentPlotItem.setLabel('top', text=self.ui.lineEdit_2.text())
                self.currentPlotWidget.title = self.ui.lineEdit_2.text()
            except:
                self.currentPlotItem.setLabel('top', text='Graph')
                self.currentPlotWidget.title = 'Graph'
            try:
                self.currentPlotItem.setLabel('left', text=self.ui.lineEdit_3.text())
                self.currentPlotWidget.yLabel = self.ui.lineEdit_3.text()
            except:
                self.currentPlotItem.setLabel('left', text='Y-Axis')
                self.currentPlotWidget.yLabel = 'Y-Axis'
            try:
                self.currentPlotItem.setLabel('bottom', text=self.ui.lineEdit_4.text())
                self.currentPlotWidget.xLabel = self.ui.lineEdit_4.text()
            except:
                self.currentPlotItem.setLabel('bottom', text='X-Axis')
                self.currentPlotWidget.xLabel = 'X-Axis'

        elif self.currentPlotWidget.type == 'Polar Plot':
            self.currentPlotWidget.xData.clear()
            self.currentPlotWidget.yData.clear()
            self.currentPlotWidget.xData.append(self.ui.comboBox_3.currentIndex())
            self.currentPlotWidget.yData.append(self.ui.comboBox_4.currentIndex())
            self.currentPlotWidget.samples = self.ui.spinBox.value()
            # Set x-range
            if self.ui.checkBox_2.isChecked():
                self.currentPlotWidget.enableAutoRange(x=self.ui.checkBox_2.isChecked())
                self.currentPlotWidget.xAutoRange = True
            else:
                try:
                    self.currentPlotWidget.enableAutoRange(x=False)
                    self.currentPlotWidget.xRange = [float(self.ui.lineEdit_10.text()), float(self.ui.lineEdit_11.text())]
                    self.currentPlotWidget.setXRange(self.currentPlotWidget.xRange[0], self.currentPlotWidget.xRange[1])
                    self.currentPlotWidget.xAutoRange = False

                except:
                    self.ui.lineEdit_10.setDisabled(True)
                    self.ui.lineEdit_11.setDisabled(True)
                    self.ui.lineEdit_10.clear()
                    self.ui.lineEdit_11.clear()
                    self.currentPlotWidget.enableAutoRange(x=True)
                    self.ui.checkBox_2.setChecked(True)
                    self.currentPlotWidget.xAutoRange = True

            # Set y-range
            if self.ui.checkBox_3.isChecked():
                self.currentPlotWidget.enableAutoRange(y=self.ui.checkBox_3.isChecked())
                self.currentPlotWidget.yAutoRange = True
            else:
                try:
                    self.currentPlotWidget.enableAutoRange(y=False)
                    self.currentPlotWidget.yRange = [float(self.ui.lineEdit_12.text()), float(self.ui.lineEdit_13.text())]
                    self.currentPlotWidget.setYRange(self.currentPlotWidget.yRange[0], self.currentPlotWidget.yRange[1])
                    self.currentPlotWidget.yAutoRange = False
                except:
                    self.ui.lineEdit_12.setDisabled(True)
                    self.ui.lineEdit_13.setDisabled(True)
                    self.ui.lineEdit_12.clear()
                    self.ui.lineEdit_13.clear()
                    self.currentPlotWidget.enableAutoRange(y=True)
                    self.ui.checkBox_3.setChecked(True)
                    self.currentPlotWidget.yAutoRange = True

            self.currentPlotItem = self.currentPlotWidget.getPlotItem()
            try:
                self.currentPlotItem.setLabel('top', text=self.ui.lineEdit_7.text())
                self.currentPlotWidget.title = self.ui.lineEdit_7.text()
            except:
                self.currentPlotItem.setLabel('top', text='Polar Plot')
                self.currentPlotWidget.title = 'Polar Plot'
            try:
                self.currentPlotItem.setLabel('left', text=self.ui.lineEdit_8.text())
                self.currentPlotWidget.yLabel = self.ui.lineEdit_8.text()
            except:
                self.currentPlotItem.setLabel('left', text='Y-Axis')
                self.currentPlotWidget.yLabel = 'Y-Axis'
            try:
                self.currentPlotItem.setLabel('bottom', text=self.ui.lineEdit_9.text())
                self.currentPlotWidget.xLabel = self.ui.lineEdit_9.text()
            except:
                self.currentPlotItem.setLabel('bottom', text='X-Axis')
                self.currentPlotWidget.xLabel = 'X-Axis'

        elif self.currentPlotWidget.type == 'Speedo Gauge':
            self.currentPlotWidget.yData.clear()
            self.currentPlotWidget.yData.append(self.ui.comboBox_5.currentIndex())
        elif self.currentPlotWidget.type == 'RPM Gauge':
            self.currentPlotWidget.yData.clear()
            self.currentPlotWidget.yData.append(self.ui.comboBox.currentIndex())
            pass

    def defaultJson(self):
        while (self.ui.tableWidget.rowCount() > 0):
            self.ui.tableWidget.removeRow(0)

        p = 0
        with open(self.defaultFile) as json_file:
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
        self.ui.listWidget.addItem("None Selected")
        with open('itemslogged.json', 'w+') as jsonlist:
            data = {}
            data['logged'] = []
            json.dump(data, jsonlist, indent=4)
            jsonlist.close()

    def canJson(self):
        p = 0
        filelookup = Open()
        file = filelookup.openFileNameDialog()
        self.Canfilename=file
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
            self.ui.listWidget.addItem("None Selected")
            with open('itemslogged.json', 'w+') as jsonlist:
                data = {}
                data['logged'] = []
                json.dump(data, jsonlist, indent=4)
                jsonlist.close()

    def tabletolist(self, row, column):
        found = False
        for i in range(self.ui.listWidget.count()):
            if self.ui.listWidget.item(i).text() == self.ui.tableWidget.item(row, 1).text() and self.ui.listWidget.count()<16:
                found = True
        if not found and self.ui.listWidget.count()<16:
            color = QColorDialog.getColor(QColor.fromRgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            color2 = color.getRgb()
            if self.ui.listWidget.item(0).text()=="None Selected":
                count=0
            else:
                count=self.ui.listWidget.count()
            if color.isValid():
                # If no CAN file is loaded use the default
                if self.Canfilename == '':
                    self.Canfilename = self.defaultFile
                with open(self.Canfilename, 'r+') as json_file:
                    data= json.load(json_file)
                    datafromcan=data["Haltech"][int(row)]
                    json_file.close()

                self.jsonlogged(datafromcan, str(color2), count)

                self.ui.listWidget.addItem(self.ui.tableWidget.item(row, 1).text())
                # print(self.ui.tableWidget.item(row, 1).text())

                item = self.ui.listWidget.item(self.ui.listWidget.count()-1)
                iconPixmap = QPixmap(32, 32)
                iconPixmap.fill(QColor(color))
                item.setIcon(QIcon(iconPixmap))

                for j in range(self.ui.tableWidget.columnCount()):
                    self.ui.tableWidget.item(row, j).setBackground(QColor.fromRgb(150, 150, 150))
                if self.ui.listWidget.item(0).text() == "None Selected":
                    self.ui.listWidget.takeItem(0)
            self.ui.label_36.setText(str(self.ui.listWidget.count()) + '/16 Channels Selected')
            self.ui.label_37.setText('Not Applied')
            self.ui.label_37.setStyleSheet('color: rgb(255, 0, 0);')

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
            num_of_channels = '0'
        else:
            num_of_channels = str(self.ui.listWidget.count())
        self.ui.label_36.setText(num_of_channels + '/16 Channels Selected')
        self.ui.label_37.setText('Not Applied')
        self.ui.label_37.setStyleSheet('color: rgb(255, 0, 0);')

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

class SendThread(QtCore.QThread):

    def __init__(self, sendmethod):
        QtCore.QThread.__init__(self)
        # self.MainWindow = MainWindow
        # self.GraphManager=GraphManager
        self.sendmethod = sendmethod

    def run(self):
        self.sendmethod()
        # for message in messages:
        #     if self.GraphManager.SerialModule.serialConnected:
        #         print("Sending message")
        #         self.GraphManager.SerialModule.sendCommand(message)
        #         self.msleep(300)
        #         print(message)
        # self.MainWindow.ui.apply_btn.setDisabled(False)
        # self.MainWindow.ui.apply_btn.setText('Apply')


class Worker(QRunnable):
    def __init__(self, fn, MainWindow, GraphManager):
        super(Worker, self).__init__()
        self.fn = fn
        self.MainWindow = MainWindow
        self.GraphManager = GraphManager

    @pyqtSlot()
    def run(self):
        # self.GraphManager.update()
        self.fn()


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

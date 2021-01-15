import sys
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog

from MainWindowroot import Ui_MainWindow
from FileBrowser import Open
from FileSaver import Save
from GraphManager import GraphManager
from Loader import SplashScreen as Loader


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.show()
        ## Pages
        ##Home Page
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
        ##Setup Page
        self.ui.btn_page_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.setup_page))
        self.ui.import_btn.clicked.connect(Open)

        #####color = QColorDialog.getColor()##### sets up color opening window

        ##Graph Page
        self.graphWidgets = GraphManager()
        self.ui.horizontalLayout_7.removeWidget(self.ui.frame_15)
        self.ui.horizontalLayout_7.addWidget(self.graphWidgets)
        self.ui.horizontalLayout_7.addWidget(self.ui.frame_15)

        self.ui.graph_page.setStyleSheet("background-color: rgb(35, 35, 35)")

        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_page))

        self.ui.graphtype_comboBox.currentIndexChanged.connect(self.menuchange)
        self.ui.importlayout_btn.clicked.connect(Open)
        self.ui.savelayout_btn.clicked.connect(Save)

        # Timer for testing graphing -> calls update function
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.graphWidgets.update)
        self.timer.start()



    def menuchange(self, i):
        configtext = (self.ui.graphtype_comboBox.currentText())
        if configtext == "Time Domain":
            self.ui.configMenuStack.setCurrentWidget(self.ui.timeDomain_page)
        if configtext == "Polar Plot":
            self.ui.configMenuStack.setCurrentWidget(self.ui.polarPlot_page)
        if configtext == "RPM Gauge":
            self.ui.configMenuStack.setCurrentWidget(self.ui.rpm_page)
        if configtext == "Speedo Gauge":
            self.ui.configMenuStack.setCurrentWidget(self.ui.speedo_page)

        ##Command Page
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    loader = Loader()
    loader.show()

    def loaderProgress():
        if loader.counter == 100:
            timer.stop()
            window.showMaximized()
            loader.close()
        loader.progress()

    # Sets a timer to check loading progress
    timer = QtCore.QTimer()
    timer.timeout.connect(loaderProgress)
    timer.start(5)





    sys.exit(app.exec_())

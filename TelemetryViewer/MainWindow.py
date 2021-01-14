import sys
from PyQt5 import QtWidgets, QtCore,QtGui
from PyQt5.QtWidgets import QColorDialog

from MainWindowroot import Ui_MainWindow
from FileBrowser import Open
from FileSaver import Save

class SplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
## Pages
    ##Home Page
        self.ui.btn_home.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.home_page))
    ##Setup Page
        self.ui.btn_page_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.setup_page))
        self.ui.import_btn.clicked.connect(Open)

        #####color = QColorDialog.getColor()##### sets up color opening window

    ##Graph Page
        self.ui.btn_page_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_page))
        self.ui.importlayout_btn.clicked.connect(Open)
        self.ui.savelayout_btn.clicked.connect(Save)
    ##Command Page
        self.ui.btn_page_4.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.command_page))
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SplashScreen()
    sys.exit(app.exec_())
